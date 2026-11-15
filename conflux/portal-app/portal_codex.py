"""Opt-in, single-local-user Codex app-server bridge for the Conflux Portal.

Codex runs only on explicit Start; its official JSONL app-server protocol
owns authentication, sessions, tools and approvals. This bridge does not
clone repositories, request API keys, proxy external credentials, install
dependencies, or start a network listener. It binds Codex to this checkout.
"""
from collections import deque
import json
import queue
import re
import shutil
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlsplit

THREAD_ID = re.compile(r"^[A-Za-z0-9_-]{6,120}$")
DECISIONS = frozenset(("accept", "decline"))
APPROVAL_METHODS = frozenset((
    "item/commandExecution/requestApproval", "item/fileChange/requestApproval",
))


class CodexError(Exception):
    pass


class CodexBridge:
    def __init__(self, checkout, executable=None):
        self.checkout = Path(checkout).resolve()
        self.executable = executable
        self.proc = None
        self.thread_id = None
        self.turn_id = None
        self.busy = False
        self.edit_enabled = False
        self.lock = threading.RLock()
        self.start_lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.pending = {}
        self.approvals = {}
        self.sequence = 0
        self.events = deque(maxlen=500)
        self.next_id = 0

    def binary(self):
        return self.executable or shutil.which("codex")

    def available(self):
        return bool(self.binary())

    def running(self):
        return self.proc is not None and self.proc.poll() is None

    def snapshot(self):
        with self.lock:
            return {
                "installed": self.available(),
                "running": self.running(),
                "thread": self.thread_id,
                "busy": self.busy,
                "editing": self.edit_enabled,
                "checkout": self.checkout.name,
                "pending_approvals": len(self.approvals),
                "sequence": self.sequence,
            }

    def _event(self, kind, **data):
        with self.lock:
            self.sequence += 1
            self.events.append({"seq": self.sequence, "kind": kind, **data})

    def poll(self, since=0):
        if type(since) is not int or not 0 <= since <= 1_000_000_000:
            raise CodexError("Invalid event position.")
        with self.lock:
            return {
                "events": [e for e in self.events if e["seq"] > since][-100:],
                "latest": self.sequence,
                "running": self.running(),
                "busy": self.busy,
                "thread": self.thread_id,
                "editing": self.edit_enabled,
                "pending_approvals": len(self.approvals),
            }

    def _send(self, payload):
        with self.write_lock:
            if not self.running():
                raise CodexError("Codex app-server is not running.")
            try:
                self.proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
                self.proc.stdin.flush()
            except (OSError, BrokenPipeError) as error:
                raise CodexError("Could not communicate with Codex app-server.") from error

    def _request(self, method, params, timeout=12):
        reply = queue.Queue(maxsize=1)
        with self.lock:
            self.next_id += 1
            identifier = self.next_id
            self.pending[identifier] = reply
        try:
            self._send({"id": identifier, "method": method, "params": params})
            try:
                result = reply.get(timeout=timeout)
            except queue.Empty:
                raise CodexError("Codex did not answer " + method + " in time.")
            if "error" in result:
                err = result.get("error") or {}
                message = str(err.get("message", "Unknown Codex error"))[:250]
                raise CodexError("Codex rejected " + method + ": " + message)
            return result.get("result") or {}
        finally:
            with self.lock:
                self.pending.pop(identifier, None)

    def _handle(self, msg):
        if not isinstance(msg, dict):
            return
        identifier = msg.get("id")
        method = msg.get("method")
        if identifier is not None and not method:
            with self.lock:
                waiting = self.pending.get(identifier)
            if waiting:
                try:
                    waiting.put_nowait(msg)
                except queue.Full:
                    pass
            return
        if identifier is not None and method:
            if method in APPROVAL_METHODS:
                params = msg.get("params") or {}
                item = params.get("command") or params.get("reason") or ""
                if isinstance(item, list):
                    item = " ".join(str(x) for x in item)
                with self.lock:
                    self.approvals[str(identifier)] = {
                        "id": identifier, "method": method,
                        "thread": params.get("threadId"), "turn": params.get("turnId"),
                        "command": str(item)[:900],
                        "reason": str(params.get("reason") or "")[:500],
                        "cwd": str(params.get("cwd") or "")[:220],
                    }
                self._event("approval", request_id=str(identifier),
                            method=method, description=str(item)[:900],
                            reason=str(params.get("reason") or "")[:500],
                            cwd=str(params.get("cwd") or "")[:220])
            else:
                # Unsupported interactive tool calls must fail closed.
                try:
                    self._send({"id": identifier,
                                "error": {"code": -32601, "message": "Not supported by Portal Codex client"}})
                except CodexError:
                    pass
                self._event("notice", message="Codex requested an unsupported interaction; it was declined.")
            return
        if not isinstance(method, str):
            return
        params = msg.get("params") or {}
        if method == "item/agentMessage/delta":
            delta = params.get("delta")
            if isinstance(delta, str):
                self._event("delta", text=delta[:7000], item_id=str(params.get("itemId") or ""))
        elif method == "item/completed":
            item = params.get("item") or {}
            typ = item.get("type")
            if typ == "agentMessage":
                self._event("answer", text=str(item.get("text") or "")[:16000],
                            item_id=str(item.get("id") or ""))
            elif typ == "commandExecution":
                self._event("activity", message="Command finished (" +
                            str(item.get("status") or "unknown") +
                            "): " + str(item.get("command") or "")[:400])
            elif typ == "fileChange":
                paths = [str(x.get("path") or "")[:160]
                         for x in (item.get("changes") or [])[:8] if isinstance(x, dict)]
                self._event("activity", message="File change (" +
                            str(item.get("status") or "unknown") +
                            "): " + ", ".join(paths))
        elif method == "turn/started":
            turn = params.get("turn") or {}
            with self.lock:
                self.busy = True
                self.turn_id = turn.get("id")
            self._event("turn_started")
        elif method == "turn/completed":
            turn = params.get("turn") or {}
            with self.lock:
                self.busy = False
                self.turn_id = None
                # Stale approval requests must not be left actionable.
                self.approvals.clear()
            failure = turn.get("error")
            failure_text = failure.get("message", "") if isinstance(failure, dict) else ""
            self._event("turn_finished", status=str(turn.get("status") or "unknown"),
                        error=str(failure_text)[:350])
        elif method == "account/login/completed":
            self._event("login_finished", success=bool(params.get("success")))
        elif method == "account/updated":
            self._event("account_updated", mode=str(params.get("authMode") or ""),
                        plan=str(params.get("planType") or ""))
        elif method == "error":
            err = params.get("error") or {}
            self._event("notice", message=str(err.get("message") or "Codex reported an error.")[:400])
        elif method == "serverRequest/resolved":
            # The server may resolve a request before the user responds.
            resolved = str(params.get("requestId") or "")
            with self.lock:
                self.approvals.pop(resolved, None)
            self._event("approval_resolved", request_id=resolved)
        elif method == "thread/started":
            thread = params.get("thread") or {}
            self._event("notice", message="Codex conversation started: " + str(thread.get("id") or "")[:100])

    def _reader(self):
        try:
            for raw in self.proc.stdout:
                if len(raw) > 260000:
                    continue
                try:
                    self._handle(json.loads(raw))
                except (ValueError, TypeError, AttributeError):
                    continue
        finally:
            with self.lock:
                self.busy = False
                self.approvals.clear()
            self._event("notice", message="Codex app-server stopped; restart it from the panel.")

    def start(self, resume=None):
        if resume is not None and (not isinstance(resume, str) or not THREAD_ID.fullmatch(resume)):
            raise CodexError("Invalid stored conversation ID.")
        with self.start_lock:
            if not self.running():
                binary = self.binary()
                if not binary:
                    raise CodexError("Codex CLI isn't installed on this device. See Updates & Setup for the official setup instructions.")
                if not self.checkout.is_dir():
                    raise CodexError("This Portal checkout is missing.")
                try:
                    self.proc = subprocess.Popen(
                        [binary, "app-server"], cwd=self.checkout, text=True,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, bufsize=1)
                except (OSError, ValueError) as error:
                    raise CodexError("Could not start the locally installed Codex CLI.") from error
                threading.Thread(target=self._reader, name="conflux-codex-reader", daemon=True).start()
                try:
                    self._request("initialize", {
                        "clientInfo": {"name": "conflux_portal", "title": "Conflux Portal",
                                       "version": "0.2.0"}}, timeout=15)
                    self._send({"method": "initialized", "params": {}})
                except CodexError:
                    self.proc.terminate()
                    raise
                self._event("notice", message="Official Codex app-server connected locally.")
            if resume and resume != self.thread_id:
                try:
                    self._request("thread/resume", {"threadId": resume, "excludeTurns": True})
                    self.thread_id = resume
                    self._event("notice", message="Previous Codex conversation resumed.")
                except CodexError:
                    self._event("notice", message="Saved conversation not available; start a new one.")
            auth = self._request("account/read", {"refreshToken": False})
            account = auth.get("account")
            return {**self.snapshot(), "authenticated": bool(account) or not auth.get("requiresOpenaiAuth", True),
                    "account_type": str(account.get("type") or "") if isinstance(account, dict) else "",
                    "plan": str(account.get("planType") or "") if isinstance(account, dict) else ""}

    def login(self):
        if not self.running():
            raise CodexError("Start Codex first.")
        result = self._request("account/login/start", {
            "type": "chatgpt", "useHostedLoginSuccessPage": True,
            "appBrand": "codex"}, timeout=15)
        url = result.get("authUrl")
        if not isinstance(url, str):
            raise CodexError("Codex did not provide a browser authorization link.")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in ("chatgpt.com", "auth.openai.com"):
            raise CodexError("Codex returned an unexpected login destination.")
        return {"auth_url": url, "note": "Authorize directly on ChatGPT. Coding stays in this panel afterward."}

    def start_thread(self):
        if not self.running():
            raise CodexError("Start Codex first.")
        if self.busy:
            raise CodexError("Finish or interrupt the active turn first.")
        result = self._request("thread/start", {
            "cwd": str(self.checkout), "approvalPolicy": "on-request",
            "sandbox": "workspace-write" if self.edit_enabled else "read-only",
        })
        thread = (result.get("thread") or {}).get("id")
        if not isinstance(thread, str) or not THREAD_ID.fullmatch(thread):
            raise CodexError("Codex did not return a usable thread ID.")
        self.thread_id = thread
        self._event("new_thread", thread=thread)
        return {"thread": thread, "editing": self.edit_enabled}

    def edits(self, allow):
        if type(allow) is not bool:
            raise CodexError("An explicit editing choice is required.")
        if self.busy:
            raise CodexError("Finish or interrupt the active turn before changing edit permissions.")
        with self.lock:
            self.edit_enabled = allow
        self._event("notice", message="Workspace editing " + ("enabled by the user." if allow else "disabled."))
        return {"editing": allow, "checkout": self.checkout.name}

    def send(self, message):
        if not self.running():
            raise CodexError("Start Codex first.")
        if self.busy:
            raise CodexError("Codex is finishing another request.")
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 2000:
            raise CodexError("Enter a message of at most 2,000 characters.")
        if not self.thread_id:
            self.start_thread()
        with self.lock:
            self.busy = True
        try:
            result = self._request("turn/start", {
                "threadId": self.thread_id,
                "input": [{"type": "text", "text": message.strip()}],
                "cwd": str(self.checkout),
                "approvalPolicy": "on-request",
                "sandboxPolicy": {
                    "type": "workspaceWrite", "writableRoots": [str(self.checkout)],
                    "networkAccess": False,
                } if self.edit_enabled else {"type": "readOnly"},
            }, timeout=25)
            turn = (result.get("turn") or {}).get("id")
            if isinstance(turn, str):
                self.turn_id = turn
            return {"accepted": True, "thread": self.thread_id, "editing": self.edit_enabled}
        except CodexError:
            with self.lock:
                self.busy = False
            raise

    def decide(self, identifier, decision):
        if not isinstance(identifier, str) or decision not in DECISIONS:
            raise CodexError("Only explicit accept or decline is supported.")
        with self.lock:
            approval = self.approvals.get(identifier)
            if not approval:
                raise CodexError("This approval request has expired or was already answered.")
            if not self.busy or approval["thread"] != self.thread_id:
                raise CodexError("The approval does not match the active conversation.")
            if decision == "accept" and not self.edit_enabled:
                raise CodexError("Enable workspace editing before approving elevated operations.")
            # Denials always remain available, including read-only sessions.
            self._send({"id": approval["id"], "result": {"decision": decision}})
            self.approvals.pop(identifier, None)
        self._event("approval_resolved", request_id=identifier)
        return {"answered": True, "decision": decision}

    def interrupt(self):
        if not self.running() or not self.thread_id or not self.turn_id:
            raise CodexError("No active Codex turn to interrupt.")
        self._request("turn/interrupt", {"threadId": self.thread_id, "turnId": self.turn_id})
        return {"interrupted": True}

    def stop(self):
        with self.start_lock:
            if self.running():
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            self.proc = None
            self.thread_id = None
            self.turn_id = None
            self.busy = False
            self.approvals.clear()
            self._event("notice", message="Codex stopped. No source files were deleted.")
            return {"stopped": True}

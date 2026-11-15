"""User-owned GitHub pull-request desk for the local Conflux Portal.

Public read-only browsing works without login. A merge requires a locally
authorized GitHub App user token, a fresh reviewed PR head SHA, a one-use
server-side ticket, explicit typed confirmation, and GitHub permission/rule
enforcement. Does not merge anything automatically.
"""
import json
import re
import secrets
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
COMMIT = re.compile(r"[a-f0-9]{40}\Z")
MAX_PR = 999_999_999


class PullError(Exception):
    pass


def _pr_number(value):
    if isinstance(value, bool):
        raise PullError("Invalid pull request number.")
    try:
        number = int(value)
    except (ValueError, TypeError):
        raise PullError("Invalid pull request number.")
    if not 1 <= number <= MAX_PR or str(value) != str(number):
        raise PullError("Invalid pull request number.")
    return number


class PullDesk:
    def __init__(self, repository, connections, request=None):
        self.repository = repository
        self.connections = connections
        self.request = request or self._http
        self.lock = threading.RLock()
        self.pending = None

    def selected_repo(self):
        try:
            repo = self.repository()
        except Exception:
            raise PullError("Open the Portal from a GitHub clone to browse its pull requests.")
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise PullError("The active checkout is not a supported GitHub repository.")
        return repo

    def _http(self, method, path, token=None, payload=None):
        url = "https://api.github.com" + path
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Conflux-Portal-Local",
            "X-GitHub-Api-Version": "2026-03-10",
        }
        if token:
            headers["Authorization"] = "Bearer " + token
        encoded = json.dumps(payload).encode("utf-8") if payload is not None else None
        if encoded is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, headers=headers, data=encoded, method=method)
        try:
            with urlopen(request, timeout=25) as response:
                raw = response.read(150_001)
            if len(raw) > 150_000:
                raise PullError("GitHub returned too much data for this view.")
            return json.loads(raw)
        except HTTPError as error:
            if error.code in (401, 403):
                raise PullError("GitHub refused access. Check App installation, repository permissions and token.")
            if error.code in (405, 409, 422):
                raise PullError("GitHub refused the merge: checks, reviews, branch rules, or SHA may have changed.")
            raise PullError("GitHub could not complete this request.") from error
        except (URLError, OSError, TimeoutError, ValueError) as error:
            raise PullError("GitHub could not complete this request.") from error

    def _api_path(self, repo, suffix):
        owner, name = repo.split("/")
        return "/repos/" + quote(owner) + "/" + quote(name) + suffix

    def _token_if_connected(self):
        try:
            return self.connections.github_token()
        except Exception:
            return None

    @staticmethod
    def _basic(record):
        return {
            "number": record["number"],
            "title": str(record.get("title", ""))[:180],
            "draft": bool(record.get("draft")),
            "state": record.get("state"),
            "base": record.get("base", {}).get("ref", ""),
            "head": record.get("head", {}).get("ref", ""),
            "head_sha": record.get("head", {}).get("sha", ""),
            "url": record.get("html_url", ""),
            "author": (record.get("user") or {}).get("login", ""),
        }

    def list(self):
        repo = self.selected_repo()
        token = self._token_if_connected()
        data = self.request("GET", self._api_path(repo, "/pulls?state=open&per_page=30"), token)
        if not isinstance(data, list):
            raise PullError("GitHub returned an invalid pull request list.")
        return {"repository": repo, "pulls": [self._basic(x) for x in data[:30]],
                "connected": bool(token), "truncated": len(data) == 30}

    def detail(self, value):
        number = _pr_number(value)
        repo = self.selected_repo()
        token = self._token_if_connected()
        pr = self.request("GET", self._api_path(repo, "/pulls/" + str(number)), token)
        files = self.request("GET", self._api_path(repo, "/pulls/" + str(number) + "/files?per_page=100"), token)
        if not isinstance(pr, dict) or not isinstance(files, list):
            raise PullError("GitHub returned invalid review data.")
        summary = self._basic(pr)
        if summary["state"] != "open":
            raise PullError("This pull request is not open.")
        if not COMMIT.fullmatch(summary["head_sha"]):
            raise PullError("GitHub did not return a valid head commit.")
        summary.update({
            "repository": repo, "mergeable": pr.get("mergeable"),
            "mergeable_state": pr.get("mergeable_state", "unknown"),
            "changed_files": pr.get("changed_files", 0),
            "files": [{
                "filename": str(x.get("filename", ""))[:250],
                "status": x.get("status", "unknown"),
                "additions": x.get("additions", 0),
                "deletions": x.get("deletions", 0),
            } for x in files[:75]],
            "partial_file_list": len(files) >= 100 or int(pr.get("changed_files", 0)) > 75,
            "body": str(pr.get("body") or "")[:1800],
            "review_complete": False,
        })
        ticket = secrets.token_urlsafe(24)
        with self.lock:
            self.pending = {"repo": repo, "number": number,
                            "sha": summary["head_sha"], "ticket": ticket,
                            "created": time.monotonic()}
        summary["ticket"] = ticket
        summary["merge_available"] = bool(token and pr.get("mergeable") is True
                                          and not summary["draft"]
                                          and not summary["partial_file_list"])
        summary["review_complete"] = not summary["partial_file_list"]
        return summary

    def merge(self, body):
        if not isinstance(body, dict):
            raise PullError("Invalid merge request.")
        number = _pr_number(body.get("number"))
        repo = self.selected_repo()
        expected = "MERGE #" + str(number) + " INTO " + repo
        if body.get("confirmation") != expected:
            raise PullError("The exact repository-and-PR confirmation was not supplied.")
        sha = body.get("sha")
        ticket = body.get("ticket")
        method = body.get("merge_method", "merge")
        if (not isinstance(sha, str) or not COMMIT.fullmatch(sha)
                or not isinstance(ticket, str) or method not in ("merge","squash","rebase")):
            raise PullError("Invalid merge parameters.")
        with self.lock:
            preview = self.pending
            self.pending = None
            if (not preview or time.monotonic() - preview["created"] > 600
                    or preview["repo"] != repo or preview["number"] != number
                    or preview["sha"] != sha
                    or not secrets.compare_digest(preview["ticket"], ticket)):
                raise PullError("Reopen this PR's review before requesting a merge.")
            try:
                token = self.connections.github_token()
            except Exception:
                raise PullError("Connect an authorized GitHub App before merging.")
            pr = self.request("GET", self._api_path(repo, "/pulls/" + str(number)), token)
            if (pr.get("state") != "open" or pr.get("draft")
                    or pr.get("mergeable") is not True
                    or pr.get("head", {}).get("sha") != sha):
                raise PullError("Pull request changed, is blocked, or is not mergeable; review again.")
            result = self.request(
                "PUT", self._api_path(repo, "/pulls/" + str(number) + "/merge"),
                token, {"sha": sha, "merge_method": method})
            if not isinstance(result, dict) or result.get("merged") is not True:
                raise PullError("GitHub did not confirm a completed merge.")
            return {"merged": True, "repository": repo, "number": number,
                    "sha": result.get("sha", ""), "url":
                    "https://github.com/" + repo + "/pull/" + str(number)}

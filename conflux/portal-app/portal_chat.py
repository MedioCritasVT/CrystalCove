"""Read-only, opt-in conversational adapter for the local Conflux Portal.

No model is granted Git, filesystem, shell, VOS or installation tools.
The UI keeps chat history only in browser memory, never on the server or in Git.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

NODES = {
    "limen": "transitions, humane explanations, and integration",
    "medio": "welcoming, experiential clarity, and balance",
    "ratio": "precise reasoning, engineering tests, and constraints",
    "specula": "evidence, uncertainty, and independent observation",
    "nexus": "coordination, continuity, and relevant dependencies",
}
ROOMS = frozenset((
    "home", "apps", "downloads", "vos", "library", "nodes", "tour",
    "soundtrack", "philosophy", "about-arch", "guide", "service-setup",
    "studio", "updates"
))


class ChatError(Exception):
    pass


def status():
    return {
        "ollama": {"configured": True, "label": "Local Ollama (requires running server)"},
        "openai": {"configured": bool(os.getenv("OPENAI_API_KEY")),
                   "label": "OpenAI API (requires server key)"},
        "oauth": True,
        "note": "ChatGPT local OAuth is optional; no Git write or agent tools are granted.",
    }


def validate_request(data):
    if not isinstance(data, dict):
        raise ChatError("Invalid chat request.")
    provider = data.get("provider")
    agent = data.get("agent")
    room = data.get("room")
    message = data.get("message")
    history = data.get("history", [])
    if provider not in ("ollama", "openai", "chatgpt"):
        raise ChatError("Choose a connected provider.")
    if agent not in NODES:
        raise ChatError("Choose a Node.")
    if room not in ROOMS:
        raise ChatError("Unknown Portal room.")
    if not isinstance(message, str) or not 1 <= len(message.strip()) <= 1500:
        raise ChatError("Enter a message of at most 1,500 characters.")
    if not isinstance(history, list) or len(history) > 8:
        raise ChatError("Conversation history is too long.")
    for item in history:
        if (not isinstance(item, dict) or item.get("role") not in ("user", "assistant")
                or not isinstance(item.get("content"), str)
                or not 1 <= len(item["content"]) <= 2000
                or set(item) != {"role", "content"}):
            raise ChatError("Conversation history contains an invalid message.")
    return provider, agent, room, message.strip(), history


def _chatgpt_plan_reply(messages, instructions, connections):
    """Use the opted-in ChatGPT plan with its required streaming contract."""
    from portal_auth import AuthError
    if connections is None:
        raise ChatError("Connect ChatGPT on this Portal host first.")
    try:
        token = connections.token("chatgpt")
    except AuthError as error:
        raise ChatError(str(error)) from error
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    try:
        with urlopen(Request("https://api.openai.com/v1/models", headers=headers),
                     timeout=20) as res:
            catalog = json.loads(res.read(96_000))
        entries = catalog.get("models", catalog.get("data", []))
        available = [entry.get("slug") or entry.get("id") for entry in entries
                     if isinstance(entry, dict)
                     and entry.get("visibility", "list") == "list"
                     and isinstance(entry.get("slug") or entry.get("id"), str)]
        if not available:
            raise ChatError("ChatGPT provided no available models for this connection.")
        preferred = os.getenv("CONFLUX_CHATGPT_MODEL", "")
        model = preferred if preferred in available else available[0]
        payload = {"model": model, "instructions": instructions,
                   "input": messages, "store": False, "stream": True}
        req = Request("https://api.openai.com/v1/responses",
                      data=json.dumps(payload).encode("utf-8"), method="POST",
                      headers={"Authorization": "Bearer " + token,
                               "Content-Type": "application/json",
                               "Accept": "text/event-stream"})
        parts = []
        complete = False
        total = 0
        with urlopen(req, timeout=90) as result:
            for line in result:
                total += len(line)
                if total > 2_000_000:
                    raise ChatError("The ChatGPT response stream was too large.")
                if not line.startswith(b"data: "):
                    continue
                data = line[6:].strip()
                if data == b"[DONE]":
                    continue
                event = json.loads(data)
                kind = event.get("type")
                if kind == "response.output_text.delta":
                    value = event.get("delta", "")
                    if isinstance(value, str) and sum(map(len, parts)) < 4000:
                        parts.append(value)
                elif kind == "response.completed":
                    complete = True
                    break
                elif kind in ("response.failed", "response.incomplete", "error"):
                    raise ChatError("ChatGPT did not complete the request. Check plan usage or retry.")
        if not complete:
            raise ChatError("The ChatGPT stream ended without a completed response.")
        text = "".join(parts).strip()[:4000]
        if not text:
            raise ChatError("ChatGPT returned no text.")
        return text
    except ChatError:
        raise
    except (HTTPError, URLError, TimeoutError, ValueError, OSError, KeyError) as error:
        raise ChatError("ChatGPT plan request failed. Check authorization and usage limits.") from error


def chat(data, connections=None):
    provider, agent, room, message, history = validate_request(data)
    instructions = (
        "You are speaking as a configured Conflux design lens named "
        + agent.title() + ", prioritizing " + NODES[agent] + ". "
        "You are a fallible language model, not the historical Node or a "
        "continuation of any private ChatGPT conversation. "
        "This is a conversational, READ-ONLY Portal companion. "
        "You have no access to the user's repository, local files, tools, "
        "account, system state, or past memories. The user is viewing the "
        + room + " room, but you have not read its contents. "
        "Do not claim to have inspected files or performed changes. "
        "You may suggest steps or draft text, but never imply a Git commit, "
        "test, install, or update has happened. Keep replies concise."
    )
    messages = history + [{"role": "user", "content": message}]
    if provider == "chatgpt":
        result = _chatgpt_plan_reply(messages, instructions, connections)
        return {"reply": result, "provider": provider,
                "agent": agent, "read_only": True}
    try:
        if provider == "ollama":
            endpoint = "http://127.0.0.1:11434/api/chat"
            payload = {
                "model": os.getenv("CONFLUX_STUDIO_OLLAMA_MODEL", "qwen3.5:4b"),
                "messages": [{"role": "system", "content": instructions}] + messages,
                "stream": False,
                "options": {"num_predict": 600},
            }
            headers = {"Content-Type": "application/json"}
        else:
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ChatError("OpenAI API is not configured on the Portal host.")
            endpoint = "https://api.openai.com/v1/responses"
            payload = {
                "model": os.getenv("CONFLUX_STUDIO_OPENAI_MODEL", "gpt-5-mini"),
                "instructions": instructions,
                "input": messages,
                "max_output_tokens": 600,
            }
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer " + key}
        request = Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                          method="POST", headers=headers)
        with urlopen(request, timeout=65) as response:
            raw = response.read(80_001)
        if len(raw) > 80_000:
            raise ChatError("The provider response was too large.")
        response = json.loads(raw)
        if provider == "ollama":
            result = response.get("message", {}).get("content", "")
        else:
            result = "".join(
                content.get("text", "") for output in response.get("output", [])
                for content in output.get("content", [])
                if content.get("type") == "output_text"
            )
        if not isinstance(result, str) or not result.strip():
            raise ChatError("The provider returned an empty reply.")
        return {"reply": result.strip()[:4000], "provider": provider,
                "agent": agent, "read_only": True}
    except ChatError:
        raise
    except (HTTPError, URLError, TimeoutError, ValueError, OSError, TypeError, KeyError) as error:
        # No provider response bodies or host environment details in the browser.
        raise ChatError("Could not reach the model or read its reply. Check the provider setup.") from error

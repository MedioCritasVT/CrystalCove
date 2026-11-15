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
        "oauth": False,
        "note": "No ChatGPT account sign-in, Git read/write or agent tools are connected.",
    }


def validate_request(data):
    if not isinstance(data, dict):
        raise ChatError("Invalid chat request.")
    provider = data.get("provider")
    agent = data.get("agent")
    room = data.get("room")
    message = data.get("message")
    history = data.get("history", [])
    if provider not in ("ollama", "openai"):
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


def chat(data):
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

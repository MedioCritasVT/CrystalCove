"use strict";
// Compact, opt-in chat companion. No automatic model calls or repository access.
(() => {
  const $ = id => document.getElementById(id);
  const panel = $("assistant-dock");
  if (!panel) return;
  const toggle = $("assistant-dock-toggle");
  const nav = $("assistant-open-nav");
  const log = $("assistant-log");
  const status = $("assistant-connection");
  const input = $("assistant-message");
  const form = $("assistant-form");
  const provider = $("assistant-provider");
  const agent = $("assistant-agent");
  const send = $("assistant-send");
  let history = [];
  let busy = false;

  function showDock(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    nav.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
  }
  function bubble(role, content) {
    const item = document.createElement("div");
    item.className = "assistant-bubble assistant-" + role;
    item.textContent = content; // never interpret model output as HTML
    log.append(item);
    log.scrollTop = log.scrollHeight;
  }
  function clear() {
    history = [];
    log.replaceChildren();
    bubble("system", "Read-only conversation. Select a provider, then type a message. Only the room name and text you submit are sent.");
  }
  function note(text, error = false) {
    status.textContent = text;
    status.dataset.error = error ? "true" : "false";
  }
  async function inspect() {
    try {
      const response = await fetch("/api/assistant/status", {cache:"no-store"});
      if (!response.ok) throw Error("Unavailable.");
      const data = await response.json();
      if (provider.value === "openai" && !data.openai.configured) {
        note("OpenAI API key not configured on this Portal host.", true);
      } else if (provider.value === "ollama") {
        note("Local Ollama selected. Requires Ollama running on this computer.");
      } else {
        note("OpenAI API configured. Sending a message may incur API charges.");
      }
    } catch { note("Assistant connection unavailable.", true); }
  }
  toggle.addEventListener("click", () => showDock(panel.hidden));
  nav.addEventListener("click", () => showDock(true));
  $("assistant-close").addEventListener("click", () => showDock(false));
  $("assistant-clear").addEventListener("click", clear);
  provider.addEventListener("change", () => { clear(); inspect(); });
  agent.addEventListener("change", clear);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (busy) return;
    const message = input.value.trim();
    if (!message || message.length > 1500) return;
    const previous = history.slice(-4);
    bubble("user", message);
    input.value = "";
    busy = true;
    send.disabled = true;
    note("Consulting selected provider…");
    try {
      const result = await post("/api/assistant/chat", {
        provider:provider.value, agent:agent.value,
        room:document.body.dataset.view || "home",
        message, history:previous
      });
      bubble("assistant", result.reply);
      history.push({role:"user",content:message},{role:"assistant",content:result.reply.slice(0,900)});
      history = history.slice(-4);
      note("Read-only reply from " + agent.selectedOptions[0].textContent + ".");
    } catch (error) {
      bubble("system", "The assistant could not reply: " + error.message);
      note("Connection failed; no Git files changed.", true);
    } finally {
      busy = false;
      send.disabled = false;
      input.focus();
    }
  });
  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  clear();
  inspect();
})();

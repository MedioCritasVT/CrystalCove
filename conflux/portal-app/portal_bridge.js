"use strict";
/*
 * Conflux Portal Development Bridge
 *
 * Deliberately opens the REAL ChatGPT, Codex and GitHub websites in new
 * browser tabs. No imitation chat, embedded sign-in, API key, access token,
 * repo-write credential, or external login data is ever requested here.
 */
(() => {
  const $ = id => document.getElementById(id);
  const dock = $("assistant-dock");
  const toggle = $("assistant-dock-toggle");
  const nav = $("assistant-open-nav");
  const repoField = $("bridge-repository");
  const taskField = $("bridge-task");
  const handoff = $("bridge-handoff");
  if (!dock || !toggle || !nav || !repoField || !taskField || !handoff) return;

  const UPSTREAM = "MedioCritasVT/CrystalCove";
  const KEY = "conflux-development-bridge-v1";
  const repoPattern = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
  let repository = UPSTREAM;
  let harness = "";
  let manualTask = "";
  let checkout = null;
  const urls = Object.freeze({
    chatgpt: "https://chatgpt.com/",
    codex: "https://chatgpt.com/codex/",
    upstream: "https://github.com/" + UPSTREAM,
    githubSettings: "https://github.com/settings/installations",
  });

  const safeRepo = value => {
    const name = String(value || "").trim().replace(/^https:\/\/github\.com\//i, "").replace(/\/$/, "").replace(/\.git$/i, "");
    if (!repoPattern.test(name) || name.length > 170 ||
        name.split("/").some(part => part === "." || part === ".." || part.startsWith(".") || part.endsWith("."))) {
      throw Error("Enter a GitHub repository as owner/name (or its github.com URL).");
    }
    return name;
  };

  function validHarness(value) {
    const url = new URL(value);
    if (url.username || url.password || url.hash) throw Error("Do not include credentials or fragments in a harness URL.");
    if (url.protocol === "https:") return url.href;
    if (url.protocol === "http:" && (url.hostname === "localhost" || url.hostname === "127.0.0.1" || url.hostname === "[::1]")) return url.href;
    throw Error("Harness URLs must use HTTPS, or HTTP on localhost.");
  }

  function show(message, error = false) {
    const el = $("bridge-status");
    el.textContent = message;
    el.dataset.error = String(error);
  }

  function open(opened) {
    dock.hidden = !opened;
    toggle.setAttribute("aria-expanded", String(opened));
    nav.setAttribute("aria-expanded", String(opened));
    if (opened) repoField.focus();
    else toggle.focus();
  }

  function updateLinks() {
    const base = "https://github.com/" + repository;
    const repoLink = $("bridge-open-repo");
    repoLink.href = base;
    $("bridge-open-prs").href = base + "/pulls";
    $("bridge-open-compare").href = base + "/compare";
    $("bridge-current-repo").textContent = repository;
    repoLink.setAttribute("aria-label", "Open " + repository + " on GitHub");
    const harnessLink = $("bridge-open-harness");
    harnessLink.hidden = !harness;
    if (harness) harnessLink.href = harness;
  }

  function currentRoom() {
    const room = document.body.dataset.view || "home";
    return /^[a-z-]{1,40}$/.test(room) ? room : "home";
  }

  function handoffText() {
    const task = taskField.value.trim();
    return [
      "Conflux Portal development handoff",
      "",
      "My chosen GitHub repository: https://github.com/" + repository,
      "Public upstream for reference: https://github.com/" + UPSTREAM,
      "Portal room where I began: " + currentRoom(),
      "",
      "Request: " + (task || "Help me inspect this Conflux-based project and plan a change I can review."),
      "",
      "Please use the actual repository access and coding tools available in this ChatGPT or Codex session.",
      "If I have not connected this repository to Codex, guide me through selecting it first.",
      "Work only in my authorized repository/branch; do not push to the upstream project.",
      "Explain changes, run the relevant tests where available, and prepare a reviewable branch or pull request.",
      "Ask before merging, publishing, installing dependencies, or changing my local machine.",
      "Report what was really done and what could not be verified.",
      "",
      "The Conflux Portal is a launcher and context handoff, not a substitute for authenticated ChatGPT/Codex.",
    ].join("\n");
  }

  function updateHandoff() {
    handoff.value = handoffText();
    $("bridge-copy").disabled = !handoff.value;
  }

  function save() {
    try {
      repository = safeRepo(repoField.value);
      const nextHarness = $("bridge-harness").value.trim();
      harness = nextHarness ? validHarness(nextHarness) : "";
      localStorage.setItem(KEY, JSON.stringify({repository, harness}));
      repoField.value = repository;
      $("bridge-harness").value = harness;
      updateLinks();
      updateHandoff();
      show("Workspace preference saved in this browser. Your GitHub/ChatGPT accounts were not accessed.");
    } catch(error) {
      show(error.message, true);
    }
  }

  async function copy() {
    updateHandoff();
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw Error("Clipboard is unavailable.");
      await navigator.clipboard.writeText(handoff.value);
      show("Handoff copied. Open genuine ChatGPT or Codex and paste it into your own session.");
    } catch {
      handoff.focus();
      handoff.select();
      show("Select and copy the handoff text manually (Ctrl+C). No data was sent.", true);
    }
  }

  function restore() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || "null");
      if (data && typeof data === "object") {
        repository = safeRepo(data.repository);
        harness = data.harness ? validHarness(data.harness) : "";
      }
    } catch {
      repository = UPSTREAM;
      harness = "";
    }
    repoField.value = repository;
    $("bridge-harness").value = harness;
    updateLinks();
    updateHandoff();
    try {
      const task = localStorage.getItem(KEY + "-task");
      if (task && typeof task === "string") {
        taskField.value = task.slice(0,1200);
        updateHandoff();
      }
    } catch { /* The bridge works without browser storage. */ }
  }

  function connectLocalCheckout() {
    fetch("/api/studio/status", {cache:"no-store"}).then(r => {
      if (!r.ok) throw Error("Not accessible");
      return r.json();
    }).then(data => {
      checkout = data;
      $("bridge-local-checkout").textContent = data.git_ready
        ? "This Portal runs from local checkout: " + data.repository + " · " + data.branch
        : "No GitHub checkout was detected for this local Portal.";
      $("bridge-checkout-use").hidden = !(data.git_ready && data.repository && repoPattern.test(data.repository));
    }).catch(() => {
      $("bridge-local-checkout").textContent = "Local Git checkout information is unavailable.";
    });
  }

  toggle.addEventListener("click", () => open(dock.hidden));
  nav.addEventListener("click", () => open(true));
  $("assistant-close").addEventListener("click", () => open(false));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !dock.hidden) open(false);
  });
  $("bridge-save").addEventListener("click", save);
  $("bridge-copy").addEventListener("click", copy);
  $("bridge-checkout-use").addEventListener("click", () => {
    if (!checkout?.git_ready) return;
    repoField.value = checkout.repository;
    save();
  });
  $("bridge-review-local").addEventListener("click", () => {
    open(false);
    document.querySelector('nav button[data-page="updates"]')?.click();
    $("updates-check")?.focus();
  });
  taskField.addEventListener("input", () => {
    updateHandoff();
    try { localStorage.setItem(KEY + "-task", taskField.value.slice(0,1200)); } catch {}
  });
  repoField.addEventListener("input", () => show("Save this repository before using its links or copying your handoff."));
  $("bridge-harness").addEventListener("input", () => show("Custom harness opens only at the address you enter; sign-in happens there."));
  $("bridge-chatgpt").href = urls.chatgpt;
  $("bridge-codex").href = urls.codex;
  $("bridge-fork").href = urls.upstream;
  $("bridge-github-settings").href = urls.githubSettings;
  restore();
  connectLocalCheckout();
})();

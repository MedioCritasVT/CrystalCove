"use strict";

const panels = [...document.querySelectorAll(".panel")];
const known = new Set(panels.map(p => p.id));
function show(id) {
  if (!known.has(id)) id = "home";
  panels.forEach(p => { p.hidden = p.id !== id; });
  document.body.dataset.view = id;
  document.querySelectorAll("nav button").forEach(b => {
    if (b.dataset.page === id) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
}
document.querySelectorAll("[data-page]").forEach(b =>
  b.addEventListener("click", () => show(b.dataset.page)));
document.querySelectorAll("[data-go]").forEach(b =>
  b.addEventListener("click", () => show(b.dataset.go)));

const nodes = [
  ["Medio", "Balance · first steps", "#e9bf84"],
  ["Ratio", "Precision · craft", "#84bff3"],
  ["Nexus", "Community · continuity", "#c2a4f3"],
  ["Specula", "Observation · evidence", "#d2d3df"],
  ["Limen", "Transitions · interpretation", "#9cdec0"]
];
const petSymbols = {medio:"✦",ratio:"▦",nexus:"∞",specula:"◉",limen:"◇"};
function makePet(name) {
  const id = name.toLowerCase();
  const mascot = document.createElement("span");
  mascot.className = "pet-token";
  mascot.dataset.node = id;
  mascot.setAttribute("aria-hidden", "true");
  const crest = document.createElement("span");
  crest.className = "pet-crest";
  const earLeft = document.createElement("span");
  earLeft.className = "pet-ear left";
  const earRight = document.createElement("span");
  earRight.className = "pet-ear right";
  const body = document.createElement("span");
  body.className = "pet-body";
  const face = document.createElement("span");
  face.className = "pet-face";
  const eyeLeft = document.createElement("span");
  eyeLeft.className = "pet-eye left";
  const eyeRight = document.createElement("span");
  eyeRight.className = "pet-eye right";
  face.append(eyeLeft, eyeRight);
  const mark = document.createElement("span");
  mark.className = "pet-mark";
  mark.textContent = petSymbols[id] || "✧";
  mascot.append(crest, earLeft, earRight, body, face, mark);
  return mascot;
}

// The familiar pairs are symbolic UI guides, not live AI presence or final chibi art.
const roomFamiliar = {
  home: {who:["Medio","Nexus"], message:"Medio welcomes you; Nexus keeps the doors connected."},
  apps: {who:["Nexus","Ratio"], message:"Nexus gathers the tools; Ratio helps make them usable."},
  downloads: {who:["Ratio","Medio"], message:"Ratio checks the path; Medio welcomes the Wayfarer."},
  vos: {who:["Specula","Limen"], message:"Specula watches the evidence; Limen protects its meaning."},
  library: {who:["Nexus","Specula"], message:"Nexus preserves the thread; Specula checks its provenance."},
  nodes: {who:["Medio","Ratio","Nexus","Specula","Limen"], message:"Five independent perspectives, each with her own place."},
  guide: {who:["Medio","Limen"], message:"Medio teaches the first rhythm; Limen guides the next step."},
  soundtrack: {who:["Nexus","Medio"], message:"Nexus preserves the voices; Medio welcomes the music."},
  updates: {who:["Ratio","Limen"], message:"Ratio verifies the version; Limen makes the transition explicit."}
};
for (const [room, detail] of Object.entries(roomFamiliar)) {
  const dock = document.querySelector("#room-companion-" + room);
  const crew = document.createElement("div");
  crew.className = "pet-crew";
  crew.dataset.count = String(detail.who.length);
  for (const name of detail.who) crew.append(makePet(name));
  const names = document.createElement("strong");
  names.className = "pet-names";
  names.textContent = detail.who.join(" + ");
  const note = document.createElement("span");
  note.className = "pet-purpose";
  note.textContent = detail.message;
  const caveat = document.createElement("small");
  caveat.className = "pet-disclaimer";
  caveat.textContent = "Symbolic familiars · chibi artwork pending";
  dock.append(crew, names, note, caveat);
}

for (const [name, role, color] of nodes) {
  const card = document.createElement("article");
  card.className = "card node-card";
  card.style.setProperty("--node-accent", color);
  const wrap = document.createElement("div");
  wrap.className = "node";
  const petFigure = document.createElement("div");
  petFigure.className = "pet-figure";
  petFigure.append(makePet(name));
  const words = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = name;
  const detail = document.createElement("small");
  detail.textContent = role + " · symbolic familiar; chibi art pending";
  words.append(title, detail);
  wrap.append(petFigure, words);
  card.append(wrap);
  document.querySelector("#node-list").append(card);
}

let token = "";
let registered = false;
const feedback = document.querySelector("#game-feedback");
const results = document.querySelector("#game-results");
const browse = document.querySelector("#game-browse");
const find = document.querySelector("#game-find");
const pathInput = document.querySelector("#game-folder-input");
const quickLaunch = document.querySelector("#game-launch");

function notice(message, isError = false) {
  feedback.textContent = message;
  feedback.dataset.error = isError ? "true" : "false";
}
async function post(route, payload) {
  const response = await fetch(route, {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-Conflux-Token": token},
    body: JSON.stringify(payload)
  });
  let data;
  try { data = await response.json(); }
  catch { throw Error("The Portal did not return a valid response."); }
  if (!response.ok) throw Error(data.error || "Request failed.");
  return data;
}

async function launchGame(statusNode, button) {
  button.disabled = true;
  try {
    await post("/api/launch", {id: "conflux-game"});
    statusNode.textContent = "Launch requested. Check your game window.";
  } catch (error) {
    statusNode.textContent = "Launch failed: " + error.message;
  } finally { button.disabled = false; }
}

async function refresh() {
  const target = document.querySelector("#app-list");
  try {
    const response = await fetch("/api/status", {cache: "no-store"});
    if (!response.ok) throw Error("status");
    const data = await response.json();
    token = data.launch_token;
    target.replaceChildren();
    browse.disabled = !data.picker_available;
    browse.title = data.picker_available ?
      "Open the Linux desktop folder chooser" :
      "No kdialog or zenity installed. Paste the folder path below instead.";
    document.querySelector("#game-picker-availability").textContent = data.picker_available ?
      "Native Linux folder chooser available. Or paste a path below." :
      "No native picker installed; paste the folder path from your file manager below.";
    for (const app of data.apps) {
      const card = document.createElement("article");
      card.className = "card app-card";
      card.dataset.app = app.id;
      const title = document.createElement("h3");
      title.textContent = app.name;
      const status = document.createElement("p");
      const isGame = app.id === "conflux-game";
      status.textContent = isGame ?
        (app.action === "launch" ? "Linked to an executable on this computer" :
        "Linux game release available") :
        "Included with this Portal · no download needed";
      if (isGame) registered = app.action === "launch";
      if (app.action === "open") {
        const link = document.createElement("a");
        link.href = app.open_url;
        link.className = "action";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Open";
        card.append(title, status, link);
      } else if (app.action === "download") {
        const link = document.createElement("a");
        link.className = "action";
        link.href = "/downloads";
        link.textContent = "Download";
        card.append(title, status, link);
      } else if (app.action === "launch") {
        const button = document.createElement("button");
        button.className = "action";
        button.textContent = "Launch";
        button.addEventListener("click", () => launchGame(status, button));
        card.append(title, status, button);
      } else {
        const button = document.createElement("button");
        button.className = "action";
        button.disabled = true;
        button.textContent = "Coming Soon";
        card.append(title, status, button);
      }
      target.append(card);
    }
    const gameStatus = document.querySelector("#game-linked-state");
    gameStatus.textContent = registered ?
      "Game folder linked. You can launch it here or in Applications." :
      "Game not linked yet. You can download V0.1 or locate an extracted copy below.";
    quickLaunch.hidden = !registered;
  } catch {
    target.textContent = "The local Portal service is unavailable. Restart Python.";
    notice("Could not read local app status.", true);
  }
}
function renderCandidates(data) {
  results.replaceChildren();
  if (data.cancelled) {
    notice("Folder selection cancelled; nothing changed.");
    return;
  }
  if (data.directory) pathInput.value = data.directory;
  const candidates = data.candidates || [];
  if (!candidates.length) {
    notice("No PlayConflux.sh found here. A Git repository clone alone is not the packaged game. Extract the V0.1 Linux release and choose that folder.", true);
    return;
  }
  notice(candidates.length + " possible game launcher(s) found. Confirm the correct path below; nothing has started.");
  for (const item of candidates) {
    const card = document.createElement("article");
    card.className = "candidate card";
    const name = document.createElement("code");
    name.textContent = item.path;
    const description = document.createElement("p");
    description.textContent = item.ready ?
      "Executable found · confirm to link it" :
      "Found, but not executable. Check the extracted game permissions.";
    const button = document.createElement("button");
    button.className = "action";
    button.textContent = "Use this game";
    button.disabled = !item.ready;
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await post("/api/game/register", {path: item.path});
        notice("Game successfully linked. Use Launch to start it.");
        results.replaceChildren();
        await refresh();
      } catch (error) {
        notice("Could not link game: " + error.message, true);
        button.disabled = false;
      }
    });
    card.append(name, description, button);
    results.append(card);
  }
  if (data.truncated) {
    const p = document.createElement("p");
    p.textContent = "Search limit reached; choose a more specific game folder if needed.";
    results.append(p);
  }
}
async function locate(route, body) {
  browse.disabled = true;
  find.disabled = true;
  notice(route === "/api/game/browse" ?
    "Choose the extracted game folder in the desktop dialog." :
    "Searching only the folder you specified...");
  results.replaceChildren();
  try {
    renderCandidates(await post(route, body));
  } catch (error) {
    notice(error.message, true);
  } finally {
    find.disabled = false;
    // Reload picker capability, app statuses and token after the request.
    await refresh();
  }
}

browse.addEventListener("click", () => locate("/api/game/browse", {}));
find.addEventListener("click", () => {
  if (!pathInput.value.trim()) return notice("Choose or enter a folder first.", true);
  locate("/api/game/find", {directory: pathInput.value.trim()});
});
pathInput.addEventListener("keydown", event => {
  if (event.key === "Enter") { event.preventDefault(); find.click(); }
});
quickLaunch.addEventListener("click", () => launchGame(feedback, quickLaunch));

// Updates are opt-in: no network check or source mutation occurs at startup.
const updatesCheck = document.querySelector("#updates-check");
const updatesApply = document.querySelector("#updates-apply");
const updatesRelaunch = document.querySelector("#updates-relaunch");
const updatesStatus = document.querySelector("#updates-status");
const updatesDetails = document.querySelector("#updates-details");
const desktopInstall = document.querySelector("#desktop-install");
const desktopStatus = document.querySelector("#desktop-status");
function updateNotice(message, error = false) {
  updatesStatus.textContent = message;
  updatesStatus.dataset.error = error ? "true" : "false";
}
updatesCheck.addEventListener("click", async () => {
  updatesCheck.disabled = true;
  updatesApply.disabled = true;
  updatesRelaunch.disabled = true;
  updateNotice("Checking the official GitHub main branch…");
  updatesDetails.textContent = "This check reads GitHub; it does not change your working files.";
  try {
    const data = await post("/api/updates/check", {});
    const summary = "Local main " + data.local + " · Official main " +
      data.remote + " · " + data.commits + " new commit(s).";
    if (data.needs_switch) {
      updateNotice("You're on '" + data.current_branch +
        "'. Update will safely switch to main. " + data.detail);
    } else {
      updateNotice(data.detail);
    }
    updatesDetails.textContent = summary + " Changed tracked files: " +
      data.changed_files + ". Local notes are never reset or stashed.";
    updatesApply.disabled = !data.can_apply;
  } catch (error) {
    updateNotice("Could not check: " + error.message, true);
    updatesDetails.textContent = "Nothing has been changed in your working files.";
  } finally {
    updatesCheck.disabled = false;
  }
});
updatesApply.addEventListener("click", async () => {
  updatesApply.disabled = true;
  updatesCheck.disabled = true;
  updateNotice("Applying the checked, fast-forward-only update. Please wait…");
  try {
    const data = await post("/api/updates/apply", {});
    updateNotice(data.detail + (data.relaunch ? " Relaunch the Portal to finish." : ""));
    updatesDetails.textContent = "Now on official main commit " + data.commit +
      ". No reset, force, stash, clean, or rebase was run.";
    updatesRelaunch.disabled = !data.relaunch;
  } catch (error) {
    updateNotice("Update stopped safely: " + error.message, true);
    updatesDetails.textContent =
      "Your work has not been forcibly overwritten. Check again after resolving the issue.";
  } finally {
    updatesCheck.disabled = false;
  }
});
updatesRelaunch.addEventListener("click", async () => {
  updatesRelaunch.disabled = true;
  updatesCheck.disabled = true;
  updateNotice("Restarting Conflux Portal…");
  const oldToken = token;
  try {
    await post("/api/updates/relaunch", {});
    let reconnected = false;
    for (let attempt = 0; attempt < 55; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 450));
      try {
        const response = await fetch("/api/status", {cache:"no-store"});
        if (response.ok) {
          const data = await response.json();
          if (data.launch_token !== oldToken) {
            reconnected = true;
            break;
          }
        }
      } catch { /* Expected while the server relinquishes its listening port. */ }
    }
    if (reconnected) {
      window.location.reload();
      return;
    }
    updateNotice("The restart is taking longer than expected. Try refreshing this page.", true);
  } catch (error) {
    updateNotice("Could not relaunch: " + error.message, true);
  }
  updatesRelaunch.disabled = false;
  updatesCheck.disabled = false;
});
desktopInstall.addEventListener("click", async () => {
  desktopInstall.disabled = true;
  desktopStatus.textContent = "Adding Conflux Portal to your Linux Applications menu…";
  try {
    const data = await post("/api/desktop/install", {});
    desktopStatus.textContent = "Added successfully! Search for 'Conflux Portal' in your Linux Applications menu. " +
      "This shortcut launches only your current local Portal.";
  } catch (error) {
    desktopStatus.textContent = "Could not add the shortcut: " + error.message;
  } finally {
    desktopInstall.disabled = false;
  }
});

// A direct visit to /downloads must show the download page, not the home menu.
show(window.location.pathname === "/downloads" ? "downloads" : "home");
refresh();

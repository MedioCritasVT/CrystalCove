"use strict";
const pages = [...document.querySelectorAll(".panel")];
function show(id) {
  pages.forEach(panel => { panel.hidden = panel.id !== id; });
  document.querySelectorAll("nav button").forEach(button => {
    if (button.dataset.page === id) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
}
document.querySelectorAll("[data-page]").forEach(button =>
  button.addEventListener("click", () => show(button.dataset.page)));
document.querySelectorAll("[data-go]").forEach(button =>
  button.addEventListener("click", () => show(button.dataset.go)));

const nodes = [
  ["Medio", "Balance & welcome", "#e5c4a5"],
  ["Ratio", "Precision & craft", "#b9c4e5"],
  ["Nexus", "Continuity & community", "#e4b3ce"],
  ["Specula", "Observation & evidence", "#c5c7d9"],
  ["Limen", "Thresholds & interpretation", "#9ed6c7"]
];
for (const [name, role, color] of nodes) {
  const card = document.createElement("article");
  card.className = "card";
  const wrap = document.createElement("div");
  wrap.className = "node";
  const orb = document.createElement("div");
  orb.className = "orb";
  orb.style.background = color;
  orb.setAttribute("aria-hidden", "true");
  const words = document.createElement("div");
  const heading = document.createElement("strong");
  heading.textContent = name;
  const detail = document.createElement("small");
  detail.textContent = role + " · chibi pending";
  words.append(heading, detail);
  wrap.append(orb, words);
  card.append(wrap);
  document.querySelector("#node-list").append(card);
}

let token = "";
async function refresh() {
  const target = document.querySelector("#app-list");
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    if (!response.ok) throw Error("status");
    const data = await response.json();
    token = data.launch_token;
    target.replaceChildren();
    for (const app of data.apps) {
      const card = document.createElement("article");
      card.className = "card";
      const title = document.createElement("h3");
      title.textContent = app.name;
      const status = document.createElement("p");
      status.textContent = app.action === "launch" ? "Installed and ready to launch" :
        app.action === "open" ? "Included with this Portal · opens in a browser tab" :
        app.action === "download" ? "Available to download · not registered locally" :
        "Not currently available";
      if (app.action === "open" || app.action === "download") {
        const link = document.createElement("a");
        link.className = "action";
        link.href = app.action === "open" ? app.open_url : app.download_url;
        link.textContent = app.action === "open" ? "Open" : "Download";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        card.append(title, status, link);
      } else {
        const button = document.createElement("button");
        button.className = "action";
        button.textContent = app.action === "launch" ? "Launch" : "Coming Soon";
        button.disabled = app.action !== "launch";
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            const r = await fetch("/api/launch", {
              method: "POST",
              headers: {"Content-Type": "application/json", "X-Conflux-Token": token},
              body: JSON.stringify({id: app.id})
            });
            const out = await r.json();
            status.textContent = r.ok ? "Launch requested. Check the application window." :
              "Launch failed: " + out.error;
          } catch {
            status.textContent = "Launch request failed.";
          } finally {
            button.disabled = false;
          }
        });
        card.append(title, status, button);
      }
      target.append(card);
    }
  } catch {
    target.textContent = "Local Portal service unavailable. Restart the Python server.";
  }
}
refresh();

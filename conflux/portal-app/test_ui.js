"use strict";
// No browser packages required: a small DOM double catches missing controls,
// broken navigation and incorrect app states before testing on Linux.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("index.html", "utf8");
const source = fs.readFileSync("app.js", "utf8");
const petCss = fs.readFileSync("familiars.css","utf8");

const panels = [...html.matchAll(/<section class="panel" id="([^"]+)"/g)].map(m => m[1]);
const navIds = [...html.matchAll(/<button data-page="([^"]+)"/g)].map(m => m[1]);
const roomIds = ["home","apps","downloads","vos","library","nodes","soundtrack","guide","updates"];
assert.deepEqual(new Set(navIds), new Set(panels));
for (const id of ["node-list", "app-list", "game-feedback", "game-results",
                  "game-browse", "game-find", "game-folder-input",
                  "game-launch", "game-linked-state", "game-picker-availability",
                   "home-game-action", "home-game-status",
                  "updates-check", "updates-apply", "updates-relaunch",
                  "updates-status", "updates-details", "portal-source-path", "desktop-install", "desktop-status",
                  ...roomIds.map(id => "room-companion-" + id)]) {
  assert(html.includes('id="' + id + '"'), "missing control " + id);
}
assert(html.includes("Conflux-V0.1-Linux-x86_64.tar.gz"));
assert(html.includes("#e9bf84") && html.includes("#c2a4f3"));
assert(html.includes("#84bff3") && html.includes("#9cdec0"));

for (const room of roomIds) {
  assert(html.includes('id="room-companion-' + room + '"'), "missing room companion: " + room);
}
assert.equal((html.match(/class="room-hero"/g) || []).length, roomIds.length);
assert(html.includes('body[data-view="vos"]') && html.includes('body[data-view="library"]'),
       "distinct room background layers missing");
assert(html.includes(".panel .room-hero h2"), "room-specific headline styling missing");
assert(petCss.includes(".pet-token .pet-face"), "visible pet artwork motif missing");
assert(petCss.includes(".pet-token .pet-hair-back") && petCss.includes(".pet-token .pet-bodice"),
       "per-character hair and wardrobe CSS missing");
assert(source.includes("nodePanels") && source.includes("View character panel"),
       "artwork references missing from Node cards");
assert(html.includes('href="/familiars.css"'), "externalized familiar styles missing");
assert(html.includes('class="nav-external"') && html.includes("github.com/MedioCritasVT/CrystalCove"),
       "direct GitHub sidebar navigation missing");
assert(!html.includes("View the portable Markdown Player Manual"),
       "outdated duplicate manual link should be removed");
assert(petCss.includes('data-node="medio"') && petCss.includes('data-node="limen"'),
       "character-specific familiar identity missing");
assert(source.includes("pet-face-mask") && source.includes("pet-headset"),
       "character face and distinctive assets missing");
assert(html.includes('<script src="/music.js"></script>'), "local player missing");
for (const id of ["music-toggle", "music-files", "music-select", "music-version",
                  "music-play", "music-prev", "music-next", "music-volume",
                  "music-audio", "music-catalog", "soundtrack-versions"]) {
  assert(html.includes('id="' + id + '"'), "missing music control " + id);
}
assert(html.includes('aria-pressed="false"'), "music must start disabled");



class Element {
  constructor(tag = "div", id = "") {
    this.tag = tag;
    this.id = id;
    this.dataset = {};
    this.attrs = {};
    this.style = {setProperty: (name, value) => { this.style[name] = value; }};
    this.children = [];
    this.handlers = {};
    this.hidden = false;
    this.disabled = false;
    this.textContent = "";
    this.value = "";
    this.href = "";
  }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = [...items]; }
  setAttribute(key, value) { this.attrs[key] = value; }
  removeAttribute(key) { delete this.attrs[key]; }
  addEventListener(event, cb) { this.handlers[event] = cb; }
  click() { return this.handlers.click?.(); }
}
const named = Object.fromEntries(
  panels.concat(["node-list", "app-list", "game-feedback", "game-results",
                  "game-browse", "game-find", "game-folder-input",
                  "game-launch", "game-linked-state", "game-picker-availability",
                   "home-game-action", "home-game-status",
                  "updates-check", "updates-apply", "updates-relaunch",
                  "updates-status", "updates-details", "portal-source-path", "desktop-install", "desktop-status",
                  ...roomIds.map(id => "room-companion-" + id)])
        .map(id => [id, new Element("div", id)])
);
const nav = navIds.map(id => {
  const button = new Element("button");
  button.dataset.page = id;
  return button;
});
const go = new Element("button");
go.dataset.go = "downloads";
const document = {
  body: {dataset: {}},
  querySelectorAll(selector) {
    return selector === ".panel" ? panels.map(id => named[id]) :
      selector === "nav button" || selector === "[data-page]" ? nav :
      selector === "[data-go]" ? [go] : [];
  },
  querySelector(selector) {
    if (!selector.startsWith("#")) throw Error("Unknown selector " + selector);
    const found = named[selector.slice(1)];
    if (!found) throw Error("Unknown id " + selector);
    return found;
  },
  createElement: tag => new Element(tag)
};
let installed = false;
const launchPath = "/home/architect/Games/Conflux/PlayConflux.sh";
const calls = [];
const fakeFetch = async (url, opts = {}) => {
  calls.push({url, opts});
  let result;
  if (url === "/api/status") {
    result = {
      launch_token: "test-only-token", picker_available: true,
       portal_root: "/home/architect/Conflux/CrystalCove/conflux/portal-app",
      apps: [
        {id:"conflux-game",name:"Conflux Game V0.1",action:installed?"launch":"download"},
        {id:"conflux-atelier",name:"Conflux Atelier",action:"open",open_url:"/apps/atelier"},
        {id:"conflux-ledger",name:"Conflux Ledger",action:"open",open_url:"/apps/ledger"}
      ]
    };
  } else if (url === "/api/game/find") {
    result = {directory:"/home/architect/Games",candidates:[{path:launchPath,ready:true}],truncated:false};
  } else if (url === "/api/game/register") {
    installed = true;
    result = {registered:true};
  } else if (url === "/api/launch") {
    result = {started:true};
  } else if (url === "/api/updates/check") {
    result = {status:"available",current_branch:"main",local:"abcdef0000",
      remote:"abcdef1111",commits:1,changed_files:2,needs_switch:false,
      can_apply:true,detail:"Update available"};
  } else if (url === "/api/updates/apply") {
    result = {updated:true,commit:"abcdef1111",relaunch:true,
      detail:"Updated official main"};
  } else if (url === "/api/desktop/install") {
    result = {installed:true,desktop_entry:"/home/demo/.local/share/applications/conflux-portal.desktop"};
  } else {
    throw Error("Unexpected request: " + url);
  }
  return {ok:true,json:async()=>result};
};
// The real HTML starts with these action buttons disabled until a check passes.
named["updates-apply"].disabled = true;
named["updates-relaunch"].disabled = true;
vm.runInNewContext(source, {document, window:{location:{pathname:"/downloads"}},fetch:fakeFetch});
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
(async () => {
  await tick();
  assert.equal(named.downloads.hidden, false, "direct /downloads must show download page");
  assert.equal(named.home.hidden, true);
  assert.equal(document.body.dataset.view, "downloads");
  assert(named["portal-source-path"].textContent.includes("CrystalCove/conflux/portal-app"),
         "active checkout path must be visible in Updates & Setup");
  assert(petCss.includes("#nodes .node-card .pet-token"), "enlarged chibi artwork styles missing");
  assert.equal(named["node-list"].children.length, 5);
  for (const id of roomIds) {
    const dock = named["room-companion-" + id];
    assert.equal(dock.children.length, 4, "missing pet ensemble for " + id);
    const crew = dock.children[0];
    assert.equal(crew.children.length, id === "nodes" ? 5 : 2);
    assert(crew.children.every(pet => pet.className === "pet-token"));
    assert(dock.children[1].textContent.length > 0, "unlabeled page companion");
  }
  const memberCards = named["node-list"].children;
  assert(memberCards.every(c => c.children[0].children[1].children.some(x => x.className === "pet-reference-link")),
          "every Node must link her source character panel");
  assert(memberCards.every(c => c.children[0].children[0].children[0].className === "pet-token"),
         "Node profiles should show the same familiar character motif");

  assert.equal(named["home-game-action"].textContent, "Get the Game");
  assert.equal(named["app-list"].children.length, 3);
  const cards = named["app-list"].children;
  assert.equal(cards[0].children[2].href, "/downloads");
  assert.equal(cards[0].children[2].textContent, "Download");
  assert.equal(cards[1].children[2].href, "/apps/atelier");
  assert.equal(cards[2].children[2].href, "/apps/ledger");
  const appNav = nav.find(n => n.dataset.page === "apps");
  appNav.click();
  assert.equal(named.apps.hidden, false);
  assert.equal(named.downloads.hidden, true);
  go.click();
  assert.equal(named.downloads.hidden, false);
  named["game-folder-input"].value = "/home/architect/Games";
  named["game-find"].click();
  await tick();
  assert.equal(named["game-results"].children.length, 1);
  assert.equal(named["game-results"].children[0].children[2].textContent, "Use this game");
  await named["game-results"].children[0].children[2].click();
  await tick();
  assert.equal(installed, true);
  assert.equal(named["game-launch"].hidden, false);
  assert.equal(named["home-game-action"].textContent, "Launch Game");
  assert(named["home-game-status"].textContent.includes("ready to launch"));
  await named["home-game-action"].click();
  assert.equal(named["app-list"].children[0].children[2].textContent, "Launch");
  await named["game-launch"].click();
  await tick();
  assert(calls.some(c => c.url === "/api/launch"), "launch must use authenticated API");
  const updatesNav = nav.find(n => n.dataset.page === "updates");
  updatesNav.click();
  assert.equal(named.updates.hidden, false);
  assert.equal(document.body.dataset.view, "updates");
  assert.equal(named["updates-apply"].disabled, true);
  await named["updates-check"].click();
  await tick();
  assert.equal(named["updates-apply"].disabled, false, "checked update must be actionable");
  assert(named["updates-status"].textContent.includes("Update available"));
  await named["updates-apply"].click();
  await tick();
  assert.equal(named["updates-relaunch"].disabled, false, "relaunch must become available");
  await named["desktop-install"].click();
  await tick();
  assert(named["desktop-status"].textContent.includes("Added successfully"));
  assert(calls.some(c => c.url === "/api/updates/check"), "update check must be explicit");
  assert(calls.some(c => c.url === "/api/updates/apply"), "update apply must be explicit");
  assert(calls.some(c => c.url === "/api/desktop/install"), "desktop entry must be opt-in");

  console.log("Portal UI smoke: navigation, palettes, release, folder search, registration, Launch, updates and desktop setup OK");
})().catch(err => {console.error(err);process.exitCode=1;});

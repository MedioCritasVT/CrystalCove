"use strict";
(() => {
  const room = document.getElementById("discovery");
  if (!room) return;
  const get = id => document.getElementById("discovery-" + id);
  const status = get("status");
  let busy = false;
  let loaded = false;
  function element(tag, text, className) {
    const item = document.createElement(tag);
    if (text !== undefined) item.textContent = text;
    if (className) item.className = className;
    return item;
  }
  function date(ns) {
    return new Date(ns / 1000000).toLocaleString();
  }
  async function request(action, payload = {}) {
    const local = await fetch("/api/status", {cache: "no-store"});
    if (!local.ok) throw new Error("Open the local Portal at its 127.0.0.1 address.");
    const {launch_token: token} = await local.json();
    if (!token) throw new Error("Local Portal authorization unavailable.");
    const response = await fetch("/api/discovery/" + action, {
      method: "POST", cache: "no-store",
      headers: {"Content-Type": "application/json", "X-Conflux-Token": token},
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Discovery request failed.");
    return result;
  }
  function controls(disabled) {
    room.querySelectorAll("button, input, select").forEach(item => { item.disabled = disabled; });
  }
  async function run(message, operation) {
    if (busy) return;
    busy = true;
    controls(true);
    status.textContent = message;
    try { await operation(); }
    catch (error) { status.textContent = error.message || "Discovery could not complete the operation."; }
    finally { busy = false; controls(false); }
  }
  function button(label, handler) {
    const item = element("button", label, "action secondary");
    item.type = "button";
    item.addEventListener("click", handler);
    return item;
  }
  async function search() {
    const payload = {query: get("query").value};
    if (get("filter").value) payload.project = get("filter").value;
    const {files} = await request("search", payload);
    const results = get("results");
    results.replaceChildren();
    if (!files.length) results.append(element("p", "No matching indexed files."));
    for (const file of files) {
      const record = element("div", undefined, "discovery-record");
      record.append(element("strong", file.path),
        element("p", file.project + " · " + Number(file.bytes).toLocaleString() + " bytes · Modified " + date(file.modified_ns), "theme-note"),
        element("p", file.root + "/" + file.path),
        element("p", "Snapshot: " + date(file.scanned_ns), "theme-note"));
      results.append(record);
    }
    status.textContent = files.length + (files.length === 100 ? "+ possible" : "") + " indexed results shown.";
  }
  async function list() {
    const {projects} = await request("projects");
    const target = get("projects");
    const filter = get("filter");
    const previous = filter.value;
    target.replaceChildren();
    filter.replaceChildren(new Option("All projects", ""));
    if (!projects.length) target.append(element("p", "No projects registered. Choose a folder above to start."));
    for (const project of projects) {
      filter.add(new Option(project.name, project.name));
      const record = element("div", undefined, "discovery-record");
      record.append(element("strong", project.name), element("p", project.root),
        element("p", project.indexed + " indexed · " + project.skipped + " skipped · Scanned " + date(project.scanned_ns), "theme-note"));
      const actions = element("div", undefined, "discovery-actions");
      actions.append(button("Refresh scan", () => run("Refreshing selected project…", async () => {
        await request("refresh", {project: project.name});
        await list(); await search();
        status.textContent = "Project refreshed.";
      })), button("Forget index", () => {
        if (!window.confirm("Forget the index for " + project.name + "? Original files remain untouched.")) return;
        run("Removing index records…", async () => {
          await request("forget", {project: project.name});
          await list(); await search();
          status.textContent = "Index records removed. Original files unchanged.";
        });
      }));
      record.append(actions); target.append(record);
    }
    if (projects.some(project => project.name === previous)) filter.value = previous;
    loaded = true;
  }
  get("register").addEventListener("submit", event => {
    event.preventDefault();
    run("Scanning selected folder…", async () => {
      const result = await request("scan", {project: get("name").value, root: get("root").value});
      await list();
      get("filter").value = result.project;
      get("query").value = "";
      await search();
      status.textContent = result.indexed + " files indexed. Original files unchanged.";
    });
  });
  get("browse").addEventListener("click", () => run("Waiting for desktop folder selection…", async () => {
    const result = await request("browse");
    if (!result.cancelled) get("root").value = result.folder;
    status.textContent = result.cancelled ? "Folder selection cancelled." : "Folder selected. Register and scan to index it.";
  }));
  get("reload").addEventListener("click", () => run("Loading index…", async () => { await list(); await search(); }));
  get("search").addEventListener("submit", event => {
    event.preventDefault(); run("Searching index…", search);
  });
  document.querySelectorAll('[data-page="discovery"], [data-go="discovery"]').forEach(item =>
    item.addEventListener("click", () => {
      if (!loaded) run("Loading local index…", async () => { await list(); await search(); });
    }));
})();

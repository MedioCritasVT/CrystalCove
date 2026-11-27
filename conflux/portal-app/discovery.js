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
  let mode = "search";
  let currentProject = "";
  let directory = "";
  let offset = 0;
  const expanded = new Set();
  let applications = [];
  let fileAssociations = {};
  let desktopExtensions = [];
  let seenRefresh = null;
  let pollTimer = null;
  let refreshInProgress = false;
  async function refreshStatus() {
    const state = await request("scan-status");
    const display = get("refresh-status");
    refreshInProgress = state.running;
    if (state.running) {
      display.textContent = "Refreshing " + state.done + "/" + state.total + (state.current ? " · " + state.current : "");
      clearTimeout(pollTimer);
      pollTimer = setTimeout(() => refreshStatus().catch(error => {display.textContent = error.message;}), 1500);
    } else {
      display.textContent = state.finished ? "Refresh complete: " + (state.done-state.errors.length) + "/" + state.total + " succeeded." + (state.errors.length ? " Previous snapshots kept for: " + state.errors.join(", ") : "") : "No batch refresh this session.";
      if (seenRefresh !== null && state.finished !== seenRefresh) {
        if (busy) {
          clearTimeout(pollTimer);
          pollTimer = setTimeout(() => refreshStatus().catch(error => {display.textContent = error.message;}), 1000);
          return;
        }
        seenRefresh = state.finished;
        await run("Updating refreshed index view…",async()=>{await list();await search();});
      }
    }
    if (seenRefresh === null) seenRefresh = state.finished;
  }
  async function loadPreferences() {
    const prefs = await request("preferences");
    get("launch-refresh").checked = prefs.launch_refresh;
    const catalog = await request("apps");
    applications = catalog.apps;
    desktopExtensions = catalog.desktop_extensions || [];
    fileAssociations = (await request("file-associations")).associations;
  }
  function appAssociation(project) {
    const holder = element("div",undefined,"discovery-association");
    const select = element("select");
    select.setAttribute("aria-label","Application for "+project.name);
    select.add(new Option("No project application",""));
    for (const app of applications.filter(a=>a.project)) select.add(new Option(app.label+(app.available?"":" (launcher not detected)"),app.id));
    select.value=project.association?.app || "";
    const directoryInput=element("input");
    directoryInput.setAttribute("aria-label","Relative application directory for "+project.name);
    directoryInput.placeholder="Project root (or relative subfolder)";
    directoryInput.value=project.association?.directory || "";
    holder.append(element("p","Project application","theme-note"),select,directoryInput,
      button("Use selected folder",()=>{if(mode==="folder" && currentProject===project.name) directoryInput.value=directory;else status.textContent="Select a folder in this project first.";}),
      button("Save association",()=>run("Saving application association…",async()=>{
        await request("associate",{project:project.name,app:select.value,directory:directoryInput.value});
        await list(); status.textContent="Application association saved.";
      })));
    return holder;
  }
  function launchProject(project) {
    if (!window.confirm("Open this trusted project in its associated application? IDEs may run project-specific configuration.")) return;
    run("Opening project application…",async()=>{
      const result = await request("open-project",{project:project.name});
      status.textContent=(result.application || "Application")+" launcher "+(result.launch_state==="running"?"is running":"accepted the request")+". Check your desktop; a window is not confirmed.";
    });
  }
  function syncSelection() {
    room.querySelectorAll(".discovery-tree-label").forEach(label => {
      const selected = mode === "folder" && label.dataset.project === currentProject && label.dataset.path === directory;
      if (selected) label.setAttribute("aria-current", "true");
      else label.removeAttribute("aria-current");
      label.closest(".discovery-tree-row").classList.toggle("is-selected", selected);
    });
  }
  function folderLabel(project, path, name, root = false) {
    const label = button("", () => browse(project, path));
    label.className = "discovery-tree-label";
    label.dataset.project = project; label.dataset.path = path;
    label.title = path || project;
    const icon = element("span", undefined, "discovery-folder-icon" + (root ? " discovery-root-icon" : ""));
    icon.setAttribute("aria-hidden", "true");
    label.append(icon, element("span", name, "discovery-folder-name"));
    return label;
  }
  function desktop(file, action, app = null) {
    if (action === "open" && !window.confirm("Open this indexed file using your desktop's associated application? Only open trusted files.")) return;
    run("Requesting desktop handoff…", async () => {
      const payload={project:file.project,path:file.path};
      if(app) payload.app=app;
      const result=await request(action,payload);
      status.textContent=(result.application || "Desktop")+" launcher "+(result.launch_state==="running"?"is running":"accepted the request")+". Check your desktop.";
    });
  }
  function record(file) {
    const row = element("div", undefined, "discovery-record discovery-file");
    const main = element("div");
    main.append(element("strong", file.name || file.path),
      element("p", file.project + " · " + Number(file.bytes).toLocaleString() + " bytes · " + date(file.modified_ns), "theme-note"),
      element("p", file.root + "/" + file.path, "discovery-location"));
    const actions = element("div", undefined, "discovery-actions");
    const suffix = /\.[^./]+$/.exec(file.path)?.[0].toLowerCase() || "";
    const choices = applications.filter(app=>app.extensions?.includes(suffix));
    if(choices.length || desktopExtensions.includes(suffix)) actions.append(button("Open", () => desktop(file, "open")));
    actions.append(button("Reveal", () => desktop(file, "reveal")));
    if(choices.length){
      const select=element("select");
      select.setAttribute("aria-label","Open "+(file.name||file.path)+" with");
      select.add(new Option("Automatic / recommended",""));
      if(desktopExtensions.includes(suffix)) select.add(new Option("Desktop default","desktop"));
      for(const app of choices) select.add(new Option(app.label+(app.available?"":" (not detected)"),app.id));
      select.value=fileAssociations[suffix] || "";
      const launch=button("Open with",()=>{
        desktop(file,"open",select.value || null);
      });
      const group=element("div",undefined,"discovery-open-with");
      const remember=button("Remember "+suffix,()=>run("Saving file association…",async()=>{
        fileAssociations=(await request("set-file-association",{suffix,app:select.value})).associations;
        await view();
        status.textContent=select.value?"Default application saved for "+suffix+".":"Automatic application restored for "+suffix+".";
      }));
      remember.title="Set the default for this file extension across all registered projects, without changing KDE settings.";
      group.append(select,launch,remember); actions.append(group);
    }
    row.append(main, actions);
    return row;
  }
  function pages(more) {
    const page = get("pagination");
    page.replaceChildren();
    if (offset) page.append(button("Previous", () => run("Loading page…", async () => {offset -= 25; await view();})));
    page.append(element("span", "Page " + (Math.floor(offset / 25) + 1)));
    if (more) page.append(button("Next", () => run("Loading page…", async () => {offset += 25; await view();})));
  }
  async function view() {
    const results = get("results"), crumb = get("breadcrumb");
    results.replaceChildren(); crumb.replaceChildren(); syncSelection();
    if (mode === "folder") {
      const {entries,total} = await request("folder", {project:currentProject,directory,offset});
      const parts = directory ? directory.split("/") : [];
      crumb.append(button(currentProject, () => browse(currentProject, "")));
      parts.forEach((part,i) => {
        crumb.append(element("span"," / "),button(part, () => browse(currentProject,parts.slice(0,i+1).join("/"))));
      });
      if (!entries.length) results.append(element("p","No indexed entries in this folder."));
      for (const entry of entries) {
        if (entry.kind === "folder") {
          const row = element("div", undefined, "discovery-record discovery-branch");
          row.append(button("▸ " + entry.name, () => browse(currentProject, entry.path)));
          results.append(row);
        } else results.append(record(entry));
      }
      pages(offset + entries.length < total);
      status.textContent = total + " indexed entries in this folder.";
    } else {
      const payload = {query:get("query").value,offset};
      if (get("filter").value) payload.project = get("filter").value;
      const {files,more} = await request("search",payload);
      if (!files.length) results.append(element("p","No matching indexed files."));
      for (const file of files) results.append(record(file));
      pages(more);
      status.textContent = files.length + " indexed results shown.";
    }
  }
  function browse(project, path) {
    run("Loading indexed folder…", async () => {
      mode="folder"; currentProject=project; directory=path; offset=0;
      get("filter").value=project; expanded.add(project);
      await view();
    });
  }
  async function search() { mode="search"; offset=0; await view(); }
  function treeNodes(container, project, path, page, replace = true) {
    if (replace) container.replaceChildren();
    else container.querySelector(":scope > .discovery-more")?.remove();
    for (const node of page.entries) {
      const line = element("div", undefined, "discovery-tree-node");
      const row = element("div", undefined, "discovery-tree-row");
      const nested = element("div", undefined, "discovery-tree-children");
      nested.hidden = true;
      let loadedChildren = false;
      if (node.children) {
        const toggle = button("▸", () => {
          if (!nested.hidden) {
            nested.hidden = true; line.classList.remove("is-expanded"); toggle.textContent = "▸"; toggle.setAttribute("aria-expanded","false"); return;
          }
          if (loadedChildren) {
            nested.hidden = false; line.classList.add("is-expanded"); toggle.textContent = "▾"; toggle.setAttribute("aria-expanded","true"); return;
          }
          run("Loading folder branches…", async () => {
            const result = await request("tree", {project,directory:node.path,offset:0});
            treeNodes(nested,project,node.path,result);
            loadedChildren = true; nested.hidden = false; line.classList.add("is-expanded");
            toggle.textContent = "▾"; toggle.setAttribute("aria-expanded","true");
          });
        });
        toggle.className = "discovery-tree-toggle";
        toggle.setAttribute("aria-label","Expand or collapse "+node.path);
        toggle.setAttribute("aria-expanded","false");
        row.append(toggle);
      } else {
        const leaf = element("span","◆","discovery-endpoint");
        leaf.setAttribute("aria-label","Terminal folder");
        row.append(leaf);
      }
      const open = folderLabel(project,node.path,node.name);
      row.append(open);
      const count=element("span",node.endpoints+" · d"+node.depth,"discovery-tree-metric");
      count.title=node.endpoints+" endpoints · "+node.depth+" levels below this folder";
      row.append(count); line.append(row,nested); container.append(line);
    }
    const next=page.offset+page.entries.length;
    if(next<page.total){
      const more=button("Show next "+Math.min(25,page.total-next)+" folders",()=>run("Loading more branches…",async()=>{
        const result=await request("tree",{project,directory:path,offset:next});
        treeNodes(container,project,path,result,false);
      }));
      more.className="discovery-more action secondary"; container.append(more);
    }
    syncSelection();
  }
  async function list() {
    const {projects} = await request("projects");
    const target = get("projects"), filter=get("filter"), previous=filter.value;
    target.replaceChildren(); filter.replaceChildren(new Option("All projects",""));
    if (!projects.length) target.append(element("p","No projects registered. Choose a folder above to start."));
    for (const project of projects) {
      filter.add(new Option(project.name,project.name));
      const item=element("div",undefined,"discovery-project discovery-tree-node");
      const metrics=project.topology;
      const row=element("div",undefined,"discovery-tree-row discovery-root-row");
      const branch=element("div",undefined,"discovery-tree-children discovery-root-children");
      const tree=element("div",undefined,"discovery-folder-map");
      treeNodes(tree,project.name,"",project.tree);
      if(!project.tree.entries.length) tree.append(element("p","◆ Project root is the indexed endpoint.","theme-note"));
      const setOpen=(open)=>{
        branch.hidden=!open; item.classList.toggle("is-expanded",open);
        toggle.textContent=open?"▾":"▸"; toggle.setAttribute("aria-expanded",String(open));
        if(open) expanded.add(project.name); else expanded.delete(project.name);
      };
      const toggle=button("▸",()=>setOpen(branch.hidden));
      toggle.className="discovery-tree-toggle";
      toggle.setAttribute("aria-label","Expand or collapse project "+project.name);
      const label=folderLabel(project.name,"",project.name,true);
      label.addEventListener("click",()=>setOpen(true));
      const count=element("span",metrics.endpoints+" · d"+metrics.depth,"discovery-tree-metric");
      count.title=metrics.endpoints+" endpoints · "+metrics.depth+" levels below root";
      row.append(toggle,label,count);
      if(project.association){
        const shortcut=button("↗",()=>launchProject(project));
        shortcut.className="discovery-app-shortcut";
        shortcut.setAttribute("aria-label","Open "+project.name+" in associated application");
        shortcut.title=applications.find(a=>a.id===project.association.app)?.label || project.association.app;
        row.append(shortcut);
      }
      const metadata=element("details",undefined,"discovery-project-details");
      metadata.append(element("summary","Project details"));
      metadata.append(element("p",project.root,"discovery-location"),
        element("p",metrics.folders+" folders · "+metrics.endpoints+" endpoints · depth "+metrics.depth+(metrics.complete?"":" · inferred"),"discovery-project-metrics"),
        element("p",project.indexed+" files · "+project.skipped+" skipped · "+date(project.scanned_ns),"theme-note"));
      const actions=element("div",undefined,"discovery-actions");
      actions.append(button("Refresh scan",()=>run("Refreshing selected project…",async()=>{
        await request("refresh",{project:project.name}); await list(); await search();
        status.textContent="Project refreshed.";
      })),button("Forget index",()=>{
        if(!window.confirm("Forget the index for "+project.name+"? Original files remain untouched."))return;
        run("Removing index records…",async()=>{
          await request("forget",{project:project.name}); expanded.delete(project.name);
          await list(); await search(); status.textContent="Index records removed. Original files unchanged.";
        });
      }));
      metadata.append(appAssociation(project),actions);
      branch.append(tree,metadata); item.append(row,branch); target.append(item);
      setOpen(expanded.has(project.name));
    }
    if(projects.some(p=>p.name===previous))filter.value=previous;
    if (!loaded && projects.length) get("registration").open=false;
    loaded=true;
    syncSelection();
  }
  get("register").addEventListener("submit",event=>{
    event.preventDefault();
    run("Scanning selected folder…",async()=>{
      const result=await request("scan",{project:get("name").value,root:get("root").value});
      expanded.add(result.project); await list();
      get("filter").value=result.project; get("query").value="";
      get("registration").open=false; await search();
      status.textContent=result.indexed+" files indexed. Original files unchanged.";
    });
  });
  get("browse").addEventListener("click",()=>run("Waiting for desktop folder selection…",async()=>{
    const result=await request("browse");
    if(!result.cancelled)get("root").value=result.folder;
    status.textContent=result.cancelled?"Folder selection cancelled.":"Folder selected. Register and scan to index it.";
  }));
  get("scan-all").addEventListener("click",()=>run("Starting refresh of all registered projects…",async()=>{
    const state=await request("scan-all");
    seenRefresh=state.running?state.finished:state.finished-1;
    clearTimeout(pollTimer); pollTimer=setTimeout(()=>refreshStatus().catch(error=>{get("refresh-status").textContent=error.message;}),500);
    status.textContent="Refresh requested; existing snapshots remain available.";
  }));
  get("launch-refresh").addEventListener("change",()=>run("Saving refresh preference…",async()=>{
    try {await request("set-preferences",{launch_refresh:get("launch-refresh").checked});status.textContent="Launch refresh preference saved.";}catch(error){get("launch-refresh").checked=!get("launch-refresh").checked;throw error;}
  }));
  get("reload").addEventListener("click",()=>run("Loading index…",async()=>{await list();await search();}));
  get("search").addEventListener("submit",event=>{event.preventDefault();run("Searching index…",search);});
  document.querySelectorAll('[data-page="discovery"], [data-go="discovery"]').forEach(item=>
    item.addEventListener("click",()=>{if(!loaded)run("Loading local index…",async()=>{await loadPreferences();await list();await search();await refreshStatus();});}));
})();

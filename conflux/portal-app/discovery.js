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
  function desktop(file, action) {
    if (action === "open" && !window.confirm("Open this indexed file using your desktop's associated application? Only open trusted files.")) return;
    run("Requesting desktop handoff…", async () => {
      await request(action, {project:file.project, path:file.path});
      status.textContent = "Desktop handoff requested. The associated application may open separately.";
    });
  }
  function record(file) {
    const row = element("div", undefined, "discovery-record discovery-file");
    const main = element("div");
    main.append(element("strong", file.name || file.path),
      element("p", file.project + " · " + Number(file.bytes).toLocaleString() + " bytes · " + date(file.modified_ns), "theme-note"),
      element("p", file.root + "/" + file.path, "discovery-location"));
    const actions = element("div", undefined, "discovery-actions");
    actions.append(button("Open", () => desktop(file, "open")), button("Reveal", () => desktop(file, "reveal")));
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
    results.replaceChildren(); crumb.replaceChildren();
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
    else container.querySelector(".discovery-more")?.remove();
    for (const node of page.entries) {
      const line = element("div", undefined, "discovery-tree-node");
      const row = element("div", undefined, "discovery-tree-row");
      const nested = element("div", undefined, "discovery-tree-children");
      nested.hidden = true;
      let loadedChildren = false;
      if (node.children) {
        const toggle = button("▸", () => {
          if (!nested.hidden) {
            nested.hidden = true; toggle.textContent = "▸"; toggle.setAttribute("aria-expanded","false"); return;
          }
          if (loadedChildren) {
            nested.hidden = false; toggle.textContent = "▾"; toggle.setAttribute("aria-expanded","true"); return;
          }
          run("Loading folder branches…", async () => {
            const result = await request("tree", {project,directory:node.path,offset:0});
            treeNodes(nested,project,node.path,result);
            loadedChildren = true; nested.hidden = false;
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
      const open = button(node.name,()=>browse(project,node.path));
      open.className="discovery-tree-label";
      open.title=node.path;
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
  }
  async function list() {
    const {projects} = await request("projects");
    const target = get("projects"), filter=get("filter"), previous=filter.value;
    target.replaceChildren(); filter.replaceChildren(new Option("All projects",""));
    if (!projects.length) target.append(element("p","No projects registered. Choose a folder above to start."));
    for (const project of projects) {
      filter.add(new Option(project.name,project.name));
      const item=element("details",undefined,"discovery-project");
      item.open=expanded.has(project.name);
      item.addEventListener("toggle",()=>{if(item.open) expanded.add(project.name);else expanded.delete(project.name);});
      const metrics=project.topology;
      item.append(element("summary",project.name+" · "+project.indexed+" files"),
        element("p",metrics.folders+" folders · "+metrics.endpoints+" endpoints · depth "+metrics.depth+(metrics.complete?"":" · inferred"),"discovery-project-metrics"));
      const branch=element("div",undefined,"discovery-tree");
      branch.append(button("▸ Browse folders",()=>browse(project.name,"")),
        element("p",project.root,"discovery-location"),
        element("p",project.skipped+" skipped · "+date(project.scanned_ns),"theme-note"));
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
      const tree=element("div",undefined,"discovery-folder-map");
      treeNodes(tree,project.name,"",project.tree);
      if(!project.tree.entries.length) tree.append(element("p","◆ Project root is the indexed endpoint.","theme-note"));
      branch.append(tree,actions); item.append(branch); target.append(item);
    }
    if(projects.some(p=>p.name===previous))filter.value=previous;
    if (!loaded && projects.length) get("registration").open=false;
    loaded=true;
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
  get("reload").addEventListener("click",()=>run("Loading index…",async()=>{await list();await search();}));
  get("search").addEventListener("submit",event=>{event.preventDefault();run("Searching index…",search);});
  document.querySelectorAll('[data-page="discovery"], [data-go="discovery"]').forEach(item=>
    item.addEventListener("click",()=>{if(!loaded)run("Loading local index…",async()=>{await list();await search();});}));
})();

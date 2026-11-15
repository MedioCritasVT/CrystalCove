"use strict";
// The Studio's color work is client-side until an explicit Git publication.
// The provider never gets permission to return scripts, files or commands.
(() => {
  const fields = ["bg","side","surface","ink","muted","line","amber","violet","blue","green"];
  const baseline = {bg:"#111522",side:"#151b2a",surface:"#202638",ink:"#f5f2f6",
    muted:"#c4c4d3",line:"#53556b",amber:"#e9bf84",violet:"#c2a4f3",
    blue:"#84bff3",green:"#9cdec0"};
  const palettes = {
    "Classic Conflux": baseline,
    "Tidal": {...baseline,bg:"#101d28",side:"#152b35",surface:"#213743",
      amber:"#efd1a2",violet:"#b4c8fc",blue:"#81d2ee",green:"#a3e7d0"},
    "Ember": {...baseline,bg:"#201721",side:"#2a1d2a",surface:"#382936",
      amber:"#ffd19b",violet:"#e4b4ec",blue:"#a8cafa",green:"#ade8c4"},
    "Quiet Grove": {...baseline,bg:"#132018",side:"#1c2823",surface:"#26362c",
      amber:"#e5d5a6",violet:"#c7b7ed",blue:"#a4d9e8",green:"#a9e9ba"}
  };
  const storageKey = "conflux-personal-theme-v1";
  const $ = id => document.getElementById(id);
  const colors = $("studio-colors");
  if (!colors) return;
  let proposal = null;
  let published = null;

  function valid(palette) {
    return palette && typeof palette === "object" &&
      fields.every(k => typeof palette[k] === "string" && /^#[0-9a-fA-F]{6}$/.test(palette[k])) &&
      Object.keys(palette).length === fields.length;
  }
  function show(message, error = false) {
    const el = $("studio-status");
    el.textContent = message;
    el.dataset.error = error ? "true" : "false";
  }
  function paletteFromInputs() {
    return Object.fromEntries(fields.map(k => [k, $("studio-color-" + k).value]));
  }
  function putInputs(p) {
    for (const k of fields) $("studio-color-" + k).value = p[k];
  }
  function applyPalette(p) {
    if (!valid(p)) throw Error("Invalid theme colors.");
    for (const k of fields) document.documentElement.style.setProperty("--" + k, p[k]);
    document.body.classList.add("theme-personal");
  }
  function reset() {
    fields.forEach(k => document.documentElement.style.removeProperty("--" + k));
    document.body.classList.remove("theme-personal");
  }
  function store() {
    const theme = {name:$("studio-name").value.trim() || "My Theme",
      palette:paletteFromInputs()};
    localStorage.setItem(storageKey, JSON.stringify(theme));
    applyPalette(theme.palette);
    show("Personal theme saved in this browser profile. No repository was changed.");
  }
  const preset = $("studio-preset");
  for (const label of Object.keys(palettes)) {
    const option = document.createElement("option");
    option.value = label;
    option.textContent = label;
    preset.append(option);
  }
  for (const key of fields) {
    const label = document.createElement("label");
    label.className = "studio-color";
    label.textContent = key.charAt(0).toUpperCase() + key.slice(1);
    const color = document.createElement("input");
    color.type = "color";
    color.id = "studio-color-" + key;
    color.dataset.color = key;
    color.value = baseline[key];
    color.setAttribute("aria-label", key + " color");
    label.prepend(color);
    colors.append(label);
  }
  putInputs(baseline);
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
    if (saved && valid(saved.palette)) {
      putInputs(saved.palette);
      $("studio-name").value = String(saved.name || "My Theme").slice(0,80);
      applyPalette(saved.palette);
    }
  } catch { /* A damaged or blocked browser preference never breaks the Portal. */ }
  preset.addEventListener("change", () => {
    putInputs(palettes[preset.value]);
    applyPalette(paletteFromInputs());
    proposal = null;
    $("studio-commit").disabled = true;
    show("Palette previewed. Save locally, or prepare a new reviewed proposal.");
  });
  colors.addEventListener("input", () => {
    applyPalette(paletteFromInputs());
    proposal = null;
    $("studio-commit").disabled = true;
    show("Palette previewed but not saved or committed.");
  });
  $("studio-save").addEventListener("click", () => {
    try { store(); } catch (e) { show("Could not save browser preference: " + e.message,true); }
  });
  $("studio-reset").addEventListener("click", () => {
    reset();
    putInputs(baseline);
    localStorage.removeItem(storageKey);
    proposal = null;
    $("studio-commit").disabled = true;
    show("Default colors restored on this browser. Git records were not changed.");
  });
  $("studio-export").addEventListener("click", () => {
    const documentData = {schema:1,name:$("studio-name").value.trim() || "My Theme",
      palette:paletteFromInputs()};
    const blob = new Blob([JSON.stringify(documentData,null,2)+"\n"],{type:"application/json"});
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;link.download = "conflux-personal-theme.json";
    document.body.append(link);link.click();link.remove();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  $("studio-import").addEventListener("change", async event => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 4096) throw Error("Theme file exceeds 4 KB.");
      const data = JSON.parse(await file.text());
      if (data.schema !== 1 || !valid(data.palette)) throw Error("Unsupported theme format.");
      putInputs(data.palette);
      $("studio-name").value = String(data.name || "Imported Theme").slice(0,80);
      applyPalette(data.palette);
      proposal = null;
      $("studio-commit").disabled = true;
      show("Imported for preview. Click Save to keep it on this browser.");
    } catch (e) { show("Import refused: " + e.message,true); }
    event.target.value = "";
  });
  async function refreshGit() {
    try {
      const response = await fetch("/api/studio/status",{cache:"no-store"});
      const info = await response.json();
      $("studio-git-status").textContent = info.git_ready ?
        "Local checkout: "+info.repository+" · branch: "+info.branch :
        "Git push requires an existing clone with a GitHub origin and working Git authentication.";
    } catch {
      $("studio-git-status").textContent = "Studio backend unavailable.";
    }
  }
  $("studio-propose").addEventListener("click", async () => {
    const button = $("studio-propose");
    button.disabled = true;
    $("studio-commit").disabled = true;
    proposal = null;
    show("Preparing a bounded palette proposal…");
    try {
      const data = await post("/api/studio/propose",{
        name:$("studio-name").value.trim(),agent:$("studio-agent").value,
        provider:$("studio-provider").value,
        instruction:$("studio-instruction").value,
        palette:paletteFromInputs()
      });
      proposal = data;
      putInputs(data.palette);
      applyPalette(data.palette);
      $("studio-preview").textContent = JSON.stringify({
        name:data.name,agent:data.agent,provider:data.provider,
        palette:data.palette,checks:data.tests},null,2);
      $("studio-commit").disabled = false;
      show("Preview ready: colors and contrast validated. No files changed. Review before publishing.");
    } catch (e) { show("Proposal not prepared: "+e.message,true); }
    finally { button.disabled = false; }
  });
  $("studio-commit").addEventListener("click", async () => {
    if (!proposal || !confirm("Publish this exact palette on a NEW Git review branch? The Portal will not merge it into main.")) return;
    $("studio-commit").disabled = true;
    show("Creating isolated Git worktree, committing reviewed palette and pushing a review branch…");
    try {
      published = await post("/api/studio/publish",{
        ticket:proposal.ticket,confirmation:"PUBLISH REVIEWED THEME"});
      const link = $("studio-review-link");
      link.href = published.review_url;
      link.hidden = false;
      $("studio-checkout").disabled = false;
      show("Published "+published.branch+" at "+published.commit+
        ". Your main branch and existing unsaved files were not modified.");
      await refreshGit();
    } catch (e) {
      show("Publish stopped: "+e.message,true);
      $("studio-commit").disabled = false;
    }
  });
  $("studio-checkout").addEventListener("click", async () => {
    if (!published || !confirm("Switch this local Portal checkout to the reviewed theme branch? Git will refuse conflicting local edits.")) return;
    try {
      const response = await post("/api/studio/preview",{
        branch:published.branch,confirmation:"PREVIEW REVIEW BRANCH"});
      show(response.detail+" Use Updates & Setup → Relaunch to load and test it.");
      $("updates-relaunch").disabled = false;
      await refreshGit();
    } catch (e) { show("Preview stopped: "+e.message,true); }
  });
  $("studio-main").addEventListener("click", async () => {
    if (!confirm("Return this checkout to its existing local main branch? No reset or force will run.")) return;
    try {
      const response = await post("/api/studio/main",{confirmation:"RETURN TO MAIN"});
      $("updates-relaunch").disabled = false;
      show(response.detail+" Use Updates & Setup → Relaunch.");
      await refreshGit();
    } catch (e) { show("Return stopped: "+e.message,true); }
  });
  $("studio-verify").addEventListener("click", async () => {
    const name = $("studio-verify-slug").value.trim();
    if (!name) return show("Enter the saved theme slug.",true);
    try {
      const res = await fetch("/api/studio/theme?slug="+encodeURIComponent(name),{cache:"no-store"});
      const data = await res.json();
      if (!res.ok) throw Error(data.error || "Theme not found.");
      putInputs(data.palette);
      applyPalette(data.palette);
      $("studio-preview").textContent = JSON.stringify(data,null,2);
      show("Passed: theme exists in active checkout, schema and contrast verified. Preview applied.");
    } catch (e) { show("Theme verification failed: "+e.message,true); }
  });
  refreshGit();
})();

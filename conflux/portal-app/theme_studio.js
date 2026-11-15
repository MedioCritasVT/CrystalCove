"use strict";
// The Studio's color work is client-side until an explicit Git publication.
// The provider never gets permission to return scripts, files or commands.
(() => {
  const fields = ["bg","side","surface","ink","muted","line","amber","violet","blue","green"];
  const baseline = {bg:"#111522",side:"#151b2a",surface:"#202638",ink:"#f5f2f6",
    muted:"#c4c4d3",line:"#53556b",amber:"#e9bf84",violet:"#c2a4f3",
    blue:"#84bff3",green:"#9cdec0"};
  // Four expressive accents over ten compatible CSS color fields.
  const accents = ["amber","violet","blue","green"];
  const accentNames = {amber:"Gold",violet:"Violet",blue:"Blue",green:"Green"};
  const palettes = {
    "Classic Conflux": baseline,
    "Tidal": {...baseline,bg:"#101d28",side:"#152b35",surface:"#213743",
      amber:"#efd1a2",violet:"#b4c8fc",blue:"#81d2ee",green:"#a3e7d0"},
    "Ember": {...baseline,bg:"#201721",side:"#2a1d2a",surface:"#382936",
      amber:"#ffd19b",violet:"#e4b4ec",blue:"#a8cafa",green:"#ade8c4"},
    "Quiet Grove": {...baseline,bg:"#132018",side:"#1c2823",surface:"#26362c",
      amber:"#e5d5a6",violet:"#c7b7ed",blue:"#a4d9e8",green:"#a9e9ba"},
    "Amethyst Observatory": {...baseline,bg:"#141426",side:"#1c1c32",surface:"#292742",
      muted:"#ccc4df",line:"#615d7f",amber:"#e8c58e",violet:"#d5adff",blue:"#92c6ff",green:"#a2dec3"},
    "Rose Circuit": {...baseline,bg:"#21151e",side:"#2a1e2b",surface:"#392a39",
      ink:"#fff1f4",muted:"#e2ccd8",line:"#805e78",
      amber:"#ffcc99",violet:"#f5b1e5",blue:"#9bc4f2",green:"#a9dcc0"},
    "Sapphire Nocturne": {...baseline,bg:"#0d1828",side:"#142239",surface:"#20324b",
      ink:"#f1f7ff",muted:"#c3d4e5",line:"#57718c",
      amber:"#eacb94",violet:"#bcb9f4",blue:"#7ab8f9",green:"#85ddc9"},
    "Copper Atlas": {...baseline,bg:"#1c1715",side:"#28221f",surface:"#362e2c",
      ink:"#f9f1e5",muted:"#d4c8c1",line:"#736457",
      amber:"#f2bb83",violet:"#d6aeef",blue:"#92c8da",green:"#a8d3aa"},
    "Jade Aether": {...baseline,bg:"#0d201f",side:"#152d2a",surface:"#203d37",
      ink:"#e9fbf4",muted:"#bee1d7",line:"#547e76",
      amber:"#efd69a",violet:"#c8b9ef",blue:"#90d9e8",green:"#82e8be"},
    "Opal Twilight": {...baseline,bg:"#191821",side:"#232234",surface:"#2e3042",
      ink:"#f7f4f7",muted:"#d0ced9",line:"#6d7185",
      amber:"#f0d0af",violet:"#c0a6ec",blue:"#a7d6e9",green:"#badcca"}
  };
  const storageKey = "conflux-personal-theme-v1";
  const textureTypes = new Set(["none","parchment","constellation","grid","weave"]);
  function texture(value) {
    if (!textureTypes.has(value)) throw Error("Unrecognized Portal texture.");
    if (value === "none") delete document.body.dataset.texture;
    else document.body.dataset.texture = value;
  }
  const $ = id => document.getElementById(id);
  const colors = $("studio-colors");
  if (!colors) return;

  function valid(palette) {
    return palette && typeof palette === "object" &&
      fields.every(k => typeof palette[k] === "string" && /^#[0-9a-fA-F]{6}$/.test(palette[k])) &&
      Object.keys(palette).length === fields.length;
  }
  function show(message, error = false) {
    const el = $("studio-theme-status");
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
    texture("none");
  }
  function store() {
    const theme = {name:$("studio-name").value.trim() || "My Theme",
      texture:$("studio-texture").value, palette:paletteFromInputs()};
    localStorage.setItem(storageKey, JSON.stringify(theme));
    applyPalette(theme.palette);
    texture(theme.texture);
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
      const savedTexture = textureTypes.has(saved.texture) ? saved.texture : "none";
      $("studio-texture").value = savedTexture;
      texture(savedTexture);
    }
  } catch { /* A damaged or blocked browser preference never breaks the Portal. */ }
  preset.addEventListener("change", () => {
    putInputs(palettes[preset.value]);
    applyPalette(paletteFromInputs());
    show("Palette previewed. Save locally, or prepare a new reviewed proposal.");
  });
  $("studio-texture").addEventListener("change", () => {
    texture($("studio-texture").value);
    show("Background texture previewed. Save your theme to retain it.");
  });
  colors.addEventListener("input", () => {
    applyPalette(paletteFromInputs());
    show("Palette previewed but not saved or committed.");
  });
  $("studio-save").addEventListener("click", () => {
    try { store(); } catch (e) { show("Could not save browser preference: " + e.message,true); }
  });
  $("studio-reset").addEventListener("click", () => {
    reset();
    putInputs(baseline);
    $("studio-texture").value = "none";
    localStorage.removeItem(storageKey);
    show("Default colors restored on this browser. Git records were not changed.");
  });
  $("studio-export").addEventListener("click", () => {
    const documentData = {schema:1,name:$("studio-name").value.trim() || "My Theme",
      texture:$("studio-texture").value, palette:paletteFromInputs()};
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
      $("studio-texture").value = textureTypes.has(data.texture) ? data.texture : "none";
      texture($("studio-texture").value);
      $("studio-name").value = String(data.name || "Imported Theme").slice(0,80);
      applyPalette(data.palette);
      proposal = null;
      $("studio-commit").disabled = true;
      show("Imported for preview. Click Save to keep it on this browser.");
    } catch (e) { show("Import refused: " + e.message,true); }
    event.target.value = "";
  });
})();

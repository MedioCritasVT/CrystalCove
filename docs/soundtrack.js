"use strict";
// Public, read-only discovery. No audio autoplays; no Git checkout is needed.
(() => {
  const root = document.querySelector("#public-soundtrack-list");
  const state = document.querySelector("#public-soundtrack-status");
  if (!root || !state) return;
  const repo = "https://raw.githubusercontent.com/MedioCritasVT/CrystalCove/main/";
  const tag = "conflux-soundtrack-v0.1";
  const api = "https://api.github.com/repos/MedioCritasVT/CrystalCove/releases/tags/" + tag;
  const prefix = "https://github.com/MedioCritasVT/CrystalCove/releases/download/" + tag + "/";
  async function load() {
    let catalog;
    try {
      const response = await fetch(repo + "conflux/soundtrack/catalog.json", {cache:"no-store"});
      if (!response.ok) throw Error("catalog unavailable");
      catalog = await response.json();
    } catch {
      state.textContent = "Could not retrieve the catalog. The recorded titles remain listed below; no download availability is implied.";
      return;
    }
    const allowed = new Set(catalog.tracks.flatMap(
      track => (track.variants || []).map(v => v.release_asset_filename)));
    const available = new Set();
    try {
      const response = await fetch(api, {cache:"no-store",headers:{"Accept":"application/vnd.github+json"}});
      if (response.ok) {
        const release = await response.json();
        if (!release.draft && release.tag_name === tag) {
          for (const asset of release.assets || []) {
            if (allowed.has(asset.name) && asset.size > 0 &&
                asset.browser_download_url === prefix + asset.name) available.add(asset.name);
          }
        }
      }
    } catch { /* Offline/blocked API means no unverified downloads are shown. */ }
    const fragment = document.createDocumentFragment();
    for (const track of catalog.tracks || []) {
      const card = document.createElement("article");
      card.className = "card soundtrack-track";
      const heading = document.createElement("h3");
      heading.textContent = track.title;
      card.append(heading);
      for (const variant of track.variants || []) {
        const detail = document.createElement("p");
        const label = document.createElement("strong");
        label.textContent = variant.id.replace(/[-_]/g, " ") + ": ";
        detail.append(label);
        const filename = variant.release_asset_filename;
        if (available.has(filename)) {
          const link = document.createElement("a");
          link.href = prefix + filename;
          link.textContent = "Download MP3";
          link.rel = "noopener noreferrer";
          detail.append(link);
        } else {
          const msg = document.createElement("span");
          msg.textContent = variant.publication_status === "metadata_only_pending_file_verification" ?
            "Source received · release file not published" : "SHA-verified source · public audio upload pending";
          detail.append(msg);
        }
        card.append(detail);
      }
      fragment.append(card);
    }
    root.replaceChildren(fragment);
    state.textContent = available.size ? available.size + " verified public download(s) available. " +
      "Other tracks remain pending publication." :
      "Catalog updated; the MP3 recordings are not yet publicly downloadable here. " +
      "No Git clone is needed once the owner publishes the release assets.";
  }
  void load();
})();

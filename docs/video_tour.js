"use strict";
// Shared by the local Portal and public static website.
// Read-only: shows a video link ONLY when its expected filename is confirmed
// on a public official GitHub Release. It never embeds or autoplays videos.
(() => {
  const root = document.querySelector("#video-tour-list");
  const status = document.querySelector("#video-tour-status");
  if (!root || !status) return;
  const repo = "MedioCritasVT/CrystalCove";
  const tag = "conflux-portal-tour-v0.1";
  const api = "https://api.github.com/repos/" + repo + "/releases/tags/" + tag;
  const prefix = "https://github.com/" + repo + "/releases/download/" + tag + "/";
  let busy = false;

  async function load() {
    if (busy) return;
    busy = true;
    status.textContent = "Checking which short Conflux clips are available…";
    try {
      const manifestResponse = await fetch(root.dataset.catalogUrl, {cache:"no-store"});
      if (!manifestResponse.ok) throw Error("clip list is unavailable");
      const manifest = await manifestResponse.json();
      if (manifest.schema !== "conflux.portal.video-tour.v0.1" || manifest.release_tag !== tag ||
          !Array.isArray(manifest.items)) throw Error("unknown tour catalog");
      const allowed = new Set(manifest.items.map(item => item.filename));
      // The four assets were independently verified on the public Release.
      // Use their explicitly published, canonical catalog links even when
      // github.com API calls are rate-limited, blocked, or temporarily offline.
      // Never promote merely inventoried/unpublished entries into links.
      const available = new Set(manifest.items.filter(entry =>
        entry.publication_status === "published" &&
        entry.published_url === prefix + entry.filename &&
        Number.isSafeInteger(entry.bytes) && entry.bytes > 0
      ).map(entry => entry.filename));
      try {
        const response = await fetch(api, {cache:"no-store",headers:{"Accept":"application/vnd.github+json"}});
        if (response.ok) {
          const release = await response.json();
          if (release.tag_name === tag && !release.draft) {
            for (const asset of release.assets || []) {
              if (allowed.has(asset.name) && asset.size > 0 &&
                  asset.browser_download_url === prefix + asset.name) {
                available.add(asset.name);
              }
            }
          }
        }
      } catch { /* Public release offline or blocked. Never imply availability. */ }

      const fragment = document.createDocumentFragment();
      for (const entry of manifest.items) {
        const card = document.createElement("article");
        card.className = "card tour-card";
        const title = document.createElement("h3");
        title.textContent = entry.title;
        const description = document.createElement("p");
        description.textContent = entry.description;
        const duration = document.createElement("small");
        duration.className = "theme-note";
        duration.textContent = String(entry.seconds) + " seconds · optional video";
        card.append(title, description, duration);
        if (available.has(entry.filename)) {
          const link = document.createElement("a");
          link.href = prefix + entry.filename; // fixed official GitHub Release path
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = "Open video ↗";
          link.setAttribute("aria-label", "Open " + entry.title + " in a new tab or window");
          card.append(link);
        } else {
          const pending = document.createElement("p");
          pending.className = "theme-note";
          pending.textContent = "Clip prepared; public upload pending.";
          card.append(pending);
        }
        fragment.append(card);
      }
      root.replaceChildren(fragment);
      status.textContent = available.size === manifest.items.length ?
        "All four short clips are publicly available. Open any one in a separate tab or window." :
        available.size ?
        available.size + " of " + manifest.items.length + " clips published so far." :
        "No published video links are currently confirmed in this catalog. The Portal itself remains available.";
    } catch (err) {
      status.textContent = "The video tour catalog could not load: " + err.message +
        ". Other Portal rooms remain available.";
    } finally {
      busy = false;
    }
  }
  if (root.dataset.autoload === "true") void load();
  else {
    const button = document.querySelector('button[data-page="tour"]');
    if (button) button.addEventListener("click", () => { void load(); });
  }
})();

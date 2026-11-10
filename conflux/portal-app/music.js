"use strict";
// Local-only preview: the browser reads user-selected audio as Blob URLs.
// It does not upload recordings, auto-play, or keep file handles on disk.
(() => {
  const $ = selector => document.querySelector(selector);
  const audio = $("#music-audio");
  const toggle = $("#music-toggle");
  const files = $("#music-files");
  const select = $("#music-select");
  const version = $("#music-version");
  const previous = $("#music-prev");
  const play = $("#music-play");
  const next = $("#music-next");
  const volume = $("#music-volume");
  const status = $("#music-status");
  const stage = $("#soundtrack-versions");
  const libraryStatus = $("#music-library-status");
  const catalog = $("#music-catalog");
  const accepted = /\.(mp3|wav|ogg|m4a|flac)$/i;

  const groups = new Map();
  let enabled = false;
  let currentGroup = "";
  let currentVersion = -1;

  function baseName(filename) {
    return filename.replace(accepted, "").trim();
  }
  function groupName(name) {
    return name
      .replace(/(?:\s*\(\s*\d+\s*\))+\s*$/u, "")
      .replace(/\s*[-_ ]+\b(?:ver(?:sion)?|v|take|mix)\s*[-_ ]*\d+[a-z]?\s*$/iu, "")
      .replace(/\s*[-_ ]+\b(?:alternate|alt)\s*$/iu, "")
      .trim();
  }
  function labelVersion(filename) {
    const name = baseName(filename);
    const base = groupName(name);
    return base === name ? "Original filename" : name.slice(base.length).replace(/^[-_ ]+/, "") || name;
  }
  function setStatus(message) {
    status.textContent = message;
  }
  function freeUrls() {
    for (const items of groups.values()) {
      for (const item of items) URL.revokeObjectURL(item.url);
    }
    groups.clear();
  }
  function activeItem() {
    return groups.get(currentGroup)?.[currentVersion] || null;
  }
  function choose(group, itemIndex = 0, shouldPlay = false) {
    const choices = groups.get(group);
    if (!choices || !choices[itemIndex]) return;
    currentGroup = group;
    currentVersion = itemIndex;
    select.value = group;
    version.replaceChildren();
    choices.forEach((item, i) => {
      const option = document.createElement("option");
      option.value = String(i);
      option.textContent = labelVersion(item.file.name);
      version.append(option);
    });
    version.value = String(itemIndex);
    audio.pause();
    audio.src = choices[itemIndex].url;
    audio.load();
    updateButtons();
    if (shouldPlay && enabled) void start();
    else setStatus(group + " · ready when you are");
  }
  function updateButtons() {
    const hasFiles = groups.size > 0;
    select.disabled = !hasFiles;
    version.disabled = !hasFiles;
    previous.disabled = !hasFiles;
    next.disabled = !hasFiles;
    play.disabled = !hasFiles;
    toggle.textContent = enabled ? "Music On" : "Music Off";
    toggle.setAttribute("aria-pressed", enabled ? "true" : "false");
    play.textContent = enabled && !audio.paused ? "Pause" : "Play";
    play.setAttribute("aria-label", enabled && !audio.paused ?
      "Pause soundtrack" : "Play selected track");
  }
  async function start() {
    if (!activeItem()) return setStatus("Choose local MP3s to play first.");
    enabled = true;
    try {
      await audio.play();
      setStatus("Playing " + currentGroup + " · " + labelVersion(activeItem().file.name));
    } catch {
      setStatus("Playback was blocked; press Play again or choose another supported audio format.");
    }
    updateButtons();
  }
  function stop() {
    enabled = false;
    audio.pause();
    setStatus(activeItem() ? "Paused · " + currentGroup : "Music off · no tracks loaded");
    updateButtons();
  }
  function move(delta) {
    if (!groups.size) return;
    const names = [...groups.keys()];
    const i = names.indexOf(currentGroup);
    const name = names[(i + delta + names.length) % names.length];
    choose(name, 0, enabled);
  }
  function showLibrary() {
    select.replaceChildren();
    for (const name of groups.keys()) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.append(option);
    }
    stage.replaceChildren();
    for (const [name, items] of groups) {
      const card = document.createElement("article");
      card.className = "card soundtrack-card";
      const title = document.createElement("h3");
      title.textContent = name;
      const subtitle = document.createElement("p");
      subtitle.textContent = items.length + " local version(s) · " +
        items.map(item => item.file.name).join(" · ");
      const button = document.createElement("button");
      button.className = "action secondary";
      button.textContent = "Select this composition";
      button.addEventListener("click", () => choose(name, 0, enabled));
      card.append(title, subtitle, button);
      stage.append(card);
    }
    libraryStatus.textContent = groups.size ?
      groups.size + " local compositions loaded with " +
        [...groups.values()].reduce((n, a) => n + a.length, 0) +
        " file(s). Nothing was uploaded." :
      "No local files selected yet. The public catalog is metadata only.";
  }
  files.addEventListener("change", () => {
    // Stop audio and revoke previous URLs before replacing the playlist.
    stop();
    audio.removeAttribute("src");
    audio.load();
    freeUrls();
    const seen = new Set();
    for (const file of files.files || []) {
      if (!accepted.test(file.name) || seen.has(file.name + ":" + file.size + ":" + file.lastModified)) continue;
      seen.add(file.name + ":" + file.size + ":" + file.lastModified);
      const group = groupName(baseName(file.name)) || file.name;
      const list = groups.get(group) || [];
      list.push({file, url:URL.createObjectURL(file)});
      groups.set(group, list);
    }
    showLibrary();
    if (groups.size) choose([...groups.keys()][0]);
    else {
      currentGroup = "";
      currentVersion = -1;
      setStatus("No supported music files were selected.");
    }
    updateButtons();
    files.value = "";
  });
  toggle.addEventListener("click", () => {
    if (enabled) stop();
    else if (groups.size) void start();
    else setStatus("Choose tracks below first. Music stays off until you enable it.");
  });
  play.addEventListener("click", () => {
    if (enabled && !audio.paused) stop();
    else void start();
  });
  previous.addEventListener("click", () => move(-1));
  next.addEventListener("click", () => move(1));
  select.addEventListener("change", () => choose(select.value, 0, enabled));
  version.addEventListener("change", () => choose(currentGroup, Number(version.value), enabled));
  volume.addEventListener("input", () => { audio.volume = Number(volume.value) / 100; });
  audio.addEventListener("ended", () => move(1));
  audio.addEventListener("pause", updateButtons);
  audio.addEventListener("play", updateButtons);
  window.addEventListener("beforeunload", freeUrls);
  audio.volume = Number(volume.value) / 100;
  updateButtons();

  // The public catalog contains no audio URLs. This is informational only.
  fetch("/soundtrack/catalog.json", {cache:"no-store"})
    .then(res => res.ok ? res.json() : Promise.reject(new Error("missing catalog")))
    .then(data => {
      catalog.replaceChildren();
      for (const composition of data.tracks || []) {
        const item = document.createElement("li");
        const title = document.createElement("strong");
        title.textContent = composition.title;
        const versions = composition.variants || [];
        const detail = document.createElement("span");
        detail.textContent = " · " + versions.length + " supplied file(s), public distribution pending rights review";
        item.append(title, detail);
        catalog.append(item);
      }
    })
    .catch(() => {
      catalog.textContent = "Soundtrack catalog is unavailable in this checkout.";
    });
})();

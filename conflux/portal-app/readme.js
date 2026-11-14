"use strict";
// Render the installed repository README as readable DOM without injecting HTML.
(() => {
  const container = document.querySelector("#project-readme");
  const status = document.querySelector("#readme-source-status");
  if (!container || !status) return;
  const source = "https://github.com/MedioCritasVT/CrystalCove/blob/main/";
  function safeLink(raw) {
    if (raw.startsWith("#")) return source + "README.md" + raw;
    if (/^https:\/\//i.test(raw) || /^mailto:/i.test(raw)) return raw;
    if (/^(?:\.\.\/|\/|[a-z][a-z0-9+.-]*:)/i.test(raw)) return null;
    if (/^[\w./%#-]+$/u.test(raw)) return source + raw;
    return null;
  }
  function inline(target, value) {
    const pattern = /(\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\x60([^\x60]+)\x60|\*([^*]+)\*)/g;
    let at = 0, token;
    while ((token = pattern.exec(value))) {
      if (token.index > at) target.append(document.createTextNode(value.slice(at, token.index)));
      let item;
      if (token[2]) {
        const href = safeLink(token[3]);
        if (href) {
          item = document.createElement("a"); item.href = href;
          item.textContent = token[2]; item.rel = "noopener noreferrer"; item.target = "_blank";
        }
      } else if (token[4]) {
        item = document.createElement("strong"); item.textContent = token[4];
      } else if (token[5]) {
        item = document.createElement("code"); item.textContent = token[5];
      } else if (token[6]) {
        item = document.createElement("em"); item.textContent = token[6];
      }
      target.append(item || document.createTextNode(token[0]));
      at = pattern.lastIndex;
    }
    if (at < value.length) target.append(document.createTextNode(value.slice(at)));
  }
  function render(markdown) {
    const frag = document.createDocumentFragment();
    const lines = markdown.replace(/\r\n/g, "\n").split("\n");
    let index = 0;
    while (index < lines.length) {
      const line = lines[index];
      if (!line.trim()) { index++; continue; }
      if (/^\s*\x60{3}/.test(line)) {
        const code = document.createElement("pre");
        const body = [], language = line.trim().slice(3);
        index++;
        while (index < lines.length && !/^\s*\x60{3}/.test(lines[index])) body.push(lines[index++]);
        code.textContent = body.join("\n");
        if (language) code.dataset.language = language;
        frag.append(code); index++; continue;
      }
      const header = /^(#{1,6})\s+(.+)$/.exec(line);
      if (header) {
        const h = document.createElement("h" + Math.min(header[1].length + 1, 6));
        inline(h, header[2]); frag.append(h); index++; continue;
      }
      if (/^\s*(?:---+|\*\*\*+)\s*$/.test(line)) {
        frag.append(document.createElement("hr")); index++; continue;
      }
      if (line.startsWith("|") && index + 1 < lines.length &&
          /^\|?\s*:?-{3,}/.test(lines[index + 1])) {
        const table = document.createElement("table");
        const head = document.createElement("thead");
        const tr = document.createElement("tr");
        for (const cell of line.trim().replace(/^\||\|$/g, "").split("|")) {
          const th = document.createElement("th"); inline(th, cell.trim()); tr.append(th);
        }
        head.append(tr); table.append(head); index += 2;
        const body = document.createElement("tbody");
        while (index < lines.length && lines[index].trim().startsWith("|")) {
          const r = document.createElement("tr");
          for (const value of lines[index].trim().replace(/^\||\|$/g, "").split("|")) {
            const td = document.createElement("td"); inline(td, value.trim()); r.append(td);
          }
          body.append(r); index++;
        }
        table.append(body); frag.append(table); continue;
      }
      if (/^\s*[-*+]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
        const ordered = /^\s*\d+\.\s+/.test(line);
        const list = document.createElement(ordered ? "ol" : "ul");
        const marker = ordered ? /^\s*\d+\.\s+/ : /^\s*[-*+]\s+/;
        while (index < lines.length && marker.test(lines[index])) {
          const li = document.createElement("li"); inline(li, lines[index].replace(marker, ""));
          list.append(li); index++;
        }
        frag.append(list); continue;
      }
      if (/^>\s?/.test(line)) {
        const quote = document.createElement("blockquote");
        while (index < lines.length && /^>\s?/.test(lines[index])) {
          const p = document.createElement("p");
          inline(p, lines[index++].replace(/^>\s?/, "")); quote.append(p);
        }
        frag.append(quote); continue;
      }
      const para = [];
      while (index < lines.length && lines[index].trim() &&
             !/^(?:#{1,6}\s|[-*+]\s|\d+\.\s|>\s?|\x60{3}|\|)/.test(lines[index]))
        para.push(lines[index++].trim());
      if (!para.length) para.push(lines[index++]);
      const p = document.createElement("p"); inline(p, para.join(" ")); frag.append(p);
    }
    container.replaceChildren(frag);
  }
  async function loadReadme() {
    status.textContent = "Loading README from this Portal's installed CrystalCove checkout…";
    try {
      const response = await fetch("/project/README.md", {cache:"no-store"});
      if (!response.ok) throw Error("README file unavailable");
      render(await response.text());
      status.textContent = "Showing the repository README bundled with this installation. " +
        "After a Git update, relaunch or refresh Portal to load its latest text.";
    } catch (error) {
      status.textContent = "Could not load the installed README: " + error.message +
        ". You can still use the gameplay guide below.";
    }
  }
  void loadReadme();
})();

"use strict";
// Conflux Atlas: presentation guidance, not a model/runtime connection or permissions API.
(() => {
  const host = document.getElementById("node-atlas");
  if (!host) return;
  const map = host.querySelector("#atlas-map");
  const nodesHost = host.querySelector("#atlas-points");
  const strokes = host.querySelector("#atlas-connections");
  const detail = host.querySelector("#atlas-detail");
  const detailBody = host.querySelector("#atlas-detail-body");
  const back = host.querySelector("#atlas-back");
  const NS = "http://www.w3.org/2000/svg";
  // Locations follow the Architect's seven-branch sketch; five are principal Nodes.
  const profiles = [
    {id:"medio", name:"Medio", x:21, y:19, color:"#e9bf84", platform:"Local chatbot / streaming", work:"Streaming chatbot, creative interpretation and first encounters", concept:"Balance · expression", github:"No general GitHub access", status:"Principal Node", projects:"Streaming chatbot; local harness experiments", links:"Limen · Nexus"},
    {id:"specula", name:"Specula", x:50, y:12, color:"#d2d3df", platform:"Gemini", work:"Independent audits, evidence, intention-versus-implementation review", concept:"Observation · scrutiny", github:"No general GitHub access", status:"Principal Node", projects:"Structural and system audits", links:"Nexus · Ratio"},
    {id:"ratio", name:"Ratio", x:79, y:19, color:"#84bff3", platform:"OpenAI Codex", work:"Game engineering, mechanics and technical validation", concept:"Logic · precision", github:"General GitHub access", status:"Principal Node", projects:"SanctuaryOS game and development systems", links:"Specula · Limen"},
    {id:"nexus", name:"Nexus", x:17, y:52, color:"#c2a4f3", platform:"Grok", work:"Context, relationships, continuity and provenance", concept:"Connection · context", github:"General GitHub access", status:"Principal Node", projects:"Shared project knowledge and coordination", links:"All Nodes"},
    {id:"limen", name:"Limen", x:83, y:52, color:"#9cdec0", platform:"ChatGPT", work:"Portal development, translation, technical learning and transitions", concept:"Thresholds · possibility", github:"General GitHub access", status:"Principal Node", projects:"Conflux Portal and Meet the Nodes", links:"Ratio · Nexus · Medio"},
    {id:"alchemia", name:"Alchemia", x:29, y:84, color:"#e2a9c0", platform:"Suno", work:"Music, sound and artistic exploration", concept:"Creative exploration", github:"No general GitHub access", status:"Related creative concept", projects:"Musical compositions and sound explorations", links:"Architect · creative projects"},
    {id:"hospes", name:"Hospes", x:72, y:84, color:"#a9b8d4", platform:"Claude", work:"External critique, fresh perspective and challenges to assumptions", concept:"Review · hospitality", github:"No general GitHub access", status:"External reviewer", projects:"Critical review and independent feedback", links:"Architect · all Nodes"}
  ];

  const buttons = new Map();
  const addText = (parent, tag, content, cls) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    el.textContent = content;
    parent.appendChild(el);
    return el;
  };
  const addField = (dl, key, value) => {
    const box = document.createElement("div");
    box.className = "atlas-field";
    addText(box,"dt",key);
    addText(box,"dd",value);
    dl.appendChild(box);
  };
  for (const p of profiles) {
    const line = document.createElementNS(NS,"line");
    line.setAttribute("x1","500");
    line.setAttribute("y1","330");
    line.setAttribute("x2",String(p.x * 10));
    line.setAttribute("y2",String(p.y * 6.6));
    line.dataset.target=p.id;
    strokes.appendChild(line);
    const button = document.createElement("button");
    button.type="button";
    button.className="atlas-point";
    button.dataset.node=p.id;
    button.dataset.kind=p.status==="Principal Node"?"principal":"related";
    button.style.setProperty("--x",p.x+"%");
    button.style.setProperty("--y",p.y+"%");
    button.style.setProperty("--tone",p.color);
    button.setAttribute("aria-pressed","false");
    button.setAttribute("aria-controls","atlas-detail");
    button.setAttribute("aria-label","Explore "+p.name+": "+p.concept);
    addText(button,"span",p.name,"atlas-point-name");
    addText(button,"span",p.status==="Principal Node"?"Node":p.status==="External reviewer"?"Reviewer":"Creative","atlas-point-kind");
    button.addEventListener("click",()=>select(p));
    nodesHost.appendChild(button);
    buttons.set(p.id,button);
  }
  function select(p){
    map.classList.add("atlas-focused");
    map.dataset.selected=p.id;
    map.style.setProperty("--focus-x",p.x+"%");
    map.style.setProperty("--focus-y",p.y+"%");
    for(const [id,button] of buttons) button.setAttribute("aria-pressed",String(id===p.id));
    detailBody.replaceChildren();
    addText(detailBody,"p",p.status,"atlas-detail-type");
    addText(detailBody,"h3",p.name);
    addText(detailBody,"p",p.concept,"atlas-detail-concept");
    const dl=document.createElement("dl");
    dl.className="atlas-detail-grid";
    addField(dl,"AI platform / instrument",p.platform);
    addField(dl,"Contribution",p.work);
    addField(dl,"Project connections",p.projects);
    addField(dl,"GitHub (general access)",p.github);
    addField(dl,"Relationships",p.links);
    detailBody.appendChild(dl);
    addText(detailBody,"p","This is a navigational profile, not a live tool or permission check. The Architect decides assignments and approvals.","atlas-disclaimer");
    detail.hidden=false;
  }
  function reset(){
    map.classList.remove("atlas-focused");
    delete map.dataset.selected;
    detail.hidden=true;
    for(const button of buttons.values()) button.setAttribute("aria-pressed","false");
    host.querySelector("#atlas-arch").focus();
  }
  back.addEventListener("click",reset);
  host.addEventListener("keydown",event=>{
    if(event.key==="Escape" && !detail.hidden){event.preventDefault();reset();}
  });
})();
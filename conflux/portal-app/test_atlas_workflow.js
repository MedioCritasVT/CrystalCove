"use strict";
// Focused DOM smoke tests without browser packages or live services.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor(tag = "div") {
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this.events = {};
    this.style = {properties:{},setProperty:(k,v)=>{this.style.properties[k]=v;}};
    const classes = new Set();
    this.classList = {add:(x)=>classes.add(x),remove:(x)=>classes.delete(x),contains:(x)=>classes.has(x)};
    this.hidden = false;
    this.textContent = "";
    this.value = "";
    this.focused = false;
  }
  setAttribute(k,v){this.attributes[k]=String(v);}
  getAttribute(k){return this.attributes[k] || null;}
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  replaceChildren(...items){this.children=items;}
  addEventListener(type,cb){(this.events[type] ||= []).push(cb);}
  dispatch(type,event={}){for(const cb of this.events[type] || [])cb(event);}
  click(){this.dispatch("click");}
  focus(){this.focused=true;}
}
const createElement = (tag) => new Element(tag);
function run(file,rootId,elementIds){
  const root = new Element();
  const children = {};
  for(const id of elementIds)children["#"+id] = new Element();
  root.querySelector = id => children[id] || null;
  const document = {
    getElementById:id => id===rootId ? root : null,
    createElement,
    createElementNS:(_ns,tag)=>createElement(tag),
    createTextNode:text=>({textContent:text})
  };
  new vm.Script(fs.readFileSync(file,"utf8"),{filename:file}).runInNewContext({document});
  return {root,children};
}
{
  const {root,children:e}=run("node_atlas.js","node-atlas",[
    "atlas-map","atlas-points","atlas-connections","atlas-detail","atlas-detail-body","atlas-back","atlas-arch"
  ]);
  const points=e["#atlas-points"],lines=e["#atlas-connections"];
  assert.equal(points.children.length,7,"five principal Nodes plus two related perspectives");
  assert.equal(lines.children.length,7,"one visual connection per perspective");
  assert.equal(points.children.filter(p=>p.dataset.kind==="principal").length,5);
  const limen=points.children.find(p=>p.dataset.node==="limen");
  limen.click();
  assert.equal(limen.getAttribute("aria-pressed"),"true");
  assert.equal(e["#atlas-detail"].hidden,false);
  assert(e["#atlas-map"].classList.contains("atlas-focused"),"selection should focus visually");
  assert(e["#atlas-detail-body"].children.some(x=>x.textContent==="Limen"),"correct selected identity");
  const allText=JSON.stringify(e["#atlas-detail-body"].children);
  assert(allText.includes("Conflux Portal"),"Limen must retain Portal responsibility");
  e["#atlas-back"].click();
  assert.equal(e["#atlas-detail"].hidden,true);
  assert.equal(limen.getAttribute("aria-pressed"),"false");
  assert(e["#atlas-arch"].focused,"return moves focus to the center");
}
{
  const {children:e}=run("workflow_instrument.js","workflow-instrument",[
    "workflow-options","workflow-summary","workflow-suggestions","workflow-task","workflow-clear"
  ]);
  const options=e["#workflow-options"],summary=e["#workflow-summary"],suggestions=e["#workflow-suggestions"];
  assert.equal(options.children.length,7,"seven selectable workflow concepts");
  assert.equal(suggestions.children.length,0,"no Nodes automatically assigned");
  const choose=label=>{
    const option=options.children.find(button=>button.children.some(child=>child.textContent===label));
    assert(option,"missing concept "+label);
    option.click();
    return option;
  };
  const nodeNames=()=>suggestions.children.map(group=>
    group.children.find(child=>child.className==="workflow-node-list").children
      .map(card=>card.children.find(child=>child.className==="workflow-node-name").textContent));
  const practical=choose("Practical");
  assert.equal(practical.getAttribute("aria-pressed"),"true");
  assert.deepEqual(nodeNames(),[["Ratio","Limen","Hospes"]],"Practical follows Architect's exact associations");
  choose("Design");
  assert.deepEqual(nodeNames(),[["Ratio","Limen","Hospes"],["Medio","Nexus","Alchemia"]],
    "Design follows Architect's exact associations");
  choose("Optional support");
  assert.deepEqual(nodeNames()[2],["Limen","Alchemia","Nexus","Hospes"],
    "Optional Support offers all Architect-named alternatives");
  assert.equal(suggestions.children.length,3,"each chosen concept gets its own group");
  assert(summary.textContent.includes("3 kinds"),"summary reflects categories, not work assigned");
  assert(suggestions.children[0].children.some(child=>child.className==="workflow-provenance"&&child.textContent.includes("Architect")),
    "explicit user mapping must have provenance label");
  e["#workflow-task"].value="<script>not markup</script>";
  e["#workflow-task"].dispatch("input");
  assert(summary.textContent.includes("<script>"),"idea is a label, never HTML");
  assert.equal(nodeNames()[0][0],"Ratio","task text does not silently reroute selections");
  e["#workflow-clear"].click();
  assert.equal(suggestions.children.length,0,"clearing removes suggestions");
  assert.equal(e["#workflow-task"].value,"");
  choose("Technical");
  assert.deepEqual(nodeNames(),[["Ratio","Limen","Specula"]],"draft mapping remains explicit");
  assert(suggestions.children[0].children.some(child=>child.className==="workflow-provenance"&&child.textContent.includes("Proposed")));
}
console.log("Atlas and Workflow: selection, details, reason-to-visit mappings, return OK");

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
  const {root,children:e}=run("workflow_instrument.js","workflow-instrument",[
    "workflow-options","workflow-summary","workflow-steps","workflow-task","workflow-clear"
  ]);
  const options=e["#workflow-options"],summary=e["#workflow-summary"];
  assert.equal(options.children.length,7);
  assert.equal(e["#workflow-steps"].children.length,0,"no workflow is preassigned");
  options.children[0].click();
  options.children[2].click();
  assert.equal(e["#workflow-steps"].children.length,4,"goal + two approaches + review");
  assert(summary.textContent.includes("2 kinds"));
  e["#workflow-task"].value="<script>not markup</script>";
  e["#workflow-task"].dispatch("input");
  assert(e["#workflow-steps"].children[0].textContent.includes("<script>"),"idea is kept as text, not interpreted HTML");
  e["#workflow-clear"].click();
  assert.equal(e["#workflow-steps"].children.length,0);
  assert.equal(e["#workflow-task"].value,"");
}
console.log("Atlas and Workflow: selection, details, return and local-only outline OK");

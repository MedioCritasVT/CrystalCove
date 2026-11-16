"use strict";
// VOS Workflow Instrument: user-directed map of task concepts to possible
// perspectives. Suggestions are not assignments or 4AgentHarness actions.
(() => {
  const root = document.getElementById("workflow-instrument");
  if (!root) return;
  const choices = root.querySelector("#workflow-options");
  const summary = root.querySelector("#workflow-summary");
  const suggestions = root.querySelector("#workflow-suggestions");
  const task = root.querySelector("#workflow-task");
  const clear = root.querySelector("#workflow-clear");
  // Practical, Design, and Optional Support are Architect-provided groupings.
  // Other associations are initial proposals for the Architect to review.
  const categories = [
    {
      id:"technical", label:"Technical", symbol:"⌘",
      use:"Systems, tools, infrastructure, implementation",
      provenance:"Proposed starting connections",
      nodes:[
        ["Ratio","Engineering, code, mechanics and verification."],
        ["Limen","Translate technical choices into understandable steps."],
        ["Specula","Question implementation assumptions and evidence."]
      ]
    },
    {
      id:"practical", label:"Practical", symbol:"◈",
      use:"Planning, building, testing, doing",
      provenance:"Architect's suggested connections",
      nodes:[
        ["Ratio","Work through how to make something function."],
        ["Limen","Turn a tangled idea into usable next steps."],
        ["Hospes","Offer an outside, practical reality check."]
      ]
    },
    {
      id:"design", label:"Design", symbol:"✦",
      use:"Experience, presentation, aesthetic direction",
      provenance:"Architect's suggested connections",
      nodes:[
        ["Medio","Explore how the experience feels and welcomes people."],
        ["Nexus","Connect design decisions to the wider Conflux context."],
        ["Alchemia","Explore expressive form, atmosphere and music."]
      ]
    },
    {
      id:"problem", label:"Problem-solving", symbol:"◇",
      use:"Untangling obstacles and choosing an approach",
      provenance:"Proposed starting connections",
      nodes:[
        ["Ratio","Try precise, testable solutions."],
        ["Limen","Identify the boundary or transition causing friction."],
        ["Nexus","Find relationships and dependencies between parts."],
        ["Specula","Independently examine what the evidence supports."]
      ]
    },
    {
      id:"critical", label:"Critical thinking", symbol:"◎",
      use:"Evidence, assumptions, blind spots and review",
      provenance:"Proposed starting connections",
      nodes:[
        ["Specula","Audit claims against observable evidence and intent."],
        ["Hospes","Challenge the plan from an outside perspective."],
        ["Nexus","Check whether context and provenance were preserved."],
        ["Ratio","Evaluate whether technical claims hold up."]
      ]
    },
    {
      id:"optional", label:"Optional support", symbol:"☷",
      use:"Extra perspective, expression, context or second opinion",
      provenance:"Architect's suggested connections",
      nodes:[
        ["Limen","Offer translation, interpretation or a gentle second pass."],
        ["Alchemia","Add a musical or artistic possibility, if useful."],
        ["Nexus","Bring in additional context or connections."],
        ["Hospes","Offer an independent outside opinion."]
      ]
    },
    {
      id:"explore", label:"Exploration", symbol:"∞",
      use:"Curiosity, possibilities and unconventional connections",
      provenance:"Proposed starting connections",
      nodes:[
        ["Medio","Experiment with expression and experience."],
        ["Nexus","Trace unexpected connections across disciplines."],
        ["Alchemia","Explore artistic or musical directions."],
        ["Limen","Explore thresholds, translations and new possibilities."]
      ]
    }
  ];
  const nodeColors = Object.freeze({
    Medio:"#e9bf84", Ratio:"#84bff3", Nexus:"#c2a4f3",
    Specula:"#d2d3df", Limen:"#9cdec0", Alchemia:"#e2a9c0",
    Hospes:"#a9b8d4"
  });
  const selected = new Set();
  const buttons = new Map();

  function addText(parent,tag,text,cls){
    const item = document.createElement(tag);
    if(cls)item.className=cls;
    item.textContent=text;
    parent.appendChild(item);
    return item;
  }
  for(const category of categories){
    const b=document.createElement("button");
    b.type="button";
    b.className="workflow-choice";
    b.setAttribute("aria-pressed","false");
    b.setAttribute("aria-label",category.label+": "+category.use);
    const symbol=addText(b,"span",category.symbol,"workflow-symbol");
    symbol.setAttribute("aria-hidden","true");
    addText(b,"strong",category.label);
    addText(b,"span",category.use,"workflow-use");
    b.addEventListener("click",()=>{
      if(selected.has(category.id))selected.delete(category.id);
      else selected.add(category.id);
      render();
    });
    choices.appendChild(b);
    buttons.set(category.id,b);
  }
  function render(){
    for(const [id,button] of buttons)button.setAttribute("aria-pressed",String(selected.has(id)));
    const picked=categories.filter(category=>selected.has(category.id));
    const label=task.value.trim();
    summary.textContent=picked.length
      ? (label ? "For “"+label+"”, " : "")+
        "here are possible Nodes to visit for "+picked.length+
        (picked.length===1?" kind":" kinds")+" of work. This is not an assignment."
      : "Choose a kind of work to see which Nodes might offer a useful perspective.";
    suggestions.replaceChildren();
    for(const category of picked){
      const group=document.createElement("section");
      group.className="workflow-group";
      group.setAttribute("aria-label",category.label+" possible collaborators");
      addText(group,"h4",category.symbol+"  "+category.label);
      addText(group,"p",category.provenance,"workflow-provenance");
      const list=document.createElement("div");
      list.className="workflow-node-list";
      for(const [name,reason] of category.nodes){
        const item=document.createElement("article");
        item.className="workflow-node-card";
        item.style.setProperty("--node-color",nodeColors[name]);
        addText(item,"strong",name,"workflow-node-name");
        addText(item,"p",reason);
        list.appendChild(item);
      }
      group.appendChild(list);
      suggestions.appendChild(group);
    }
  }
  task.addEventListener("input",render);
  clear.addEventListener("click",()=>{selected.clear();task.value="";render();task.focus();});
  render();
})();

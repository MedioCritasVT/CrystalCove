"use strict";
// VOS Workflow Instrument V1: self-directed, static guidance. No AI, network,
// storage, task assignment, or 4AgentHarness connection.
(() => {
  const root = document.getElementById("workflow-instrument");
  if (!root) return;
  const choices = root.querySelector("#workflow-options");
  const summary = root.querySelector("#workflow-summary");
  const steps = root.querySelector("#workflow-steps");
  const task = root.querySelector("#workflow-task");
  const clear = root.querySelector("#workflow-clear");
  const types = [
    {id:"technical", label:"Technical", symbol:"⌘", use:"Systems, code, tools, and implementation", approach:"Identify dependencies, build a small test, then verify the result."},
    {id:"practical", label:"Practical", symbol:"◈", use:"Real-world steps, materials, setup, and execution", approach:"List what is available, choose the next physical step, and check that it works."},
    {id:"design", label:"Design", symbol:"✦", use:"Appearance, interaction, presentation, and experience", approach:"Make a rough layout, gather feedback, and revise the experience."},
    {id:"problem", label:"Problem-solving", symbol:"◇", use:"Untangling an obstacle and comparing approaches", approach:"Define the obstacle, test two possible explanations, and keep what resolves it."},
    {id:"critical", label:"Critical thinking", symbol:"◎", use:"Assumptions, evidence, risks, and independent review", approach:"Ask what is claimed, what is verified, and what evidence is missing."},
    {id:"optional", label:"Optional support", symbol:"☷", use:"Extra perspectives, accessibility, documentation, or second opinions", approach:"Decide what extra support would help without making it a prerequisite."},
    {id:"explore", label:"Exploration", symbol:"∞", use:"Possibilities and unfamiliar connections", approach:"Generate alternatives without treating any as an approved commitment."}
  ];
  const selected = new Set();
  const buttons = new Map();
  for(const t of types){
    const b=document.createElement("button");
    b.type="button";
    b.className="workflow-choice";
    b.setAttribute("aria-pressed","false");
    b.setAttribute("aria-label",t.label+": "+t.use);
    const symbol=document.createElement("span");symbol.className="workflow-symbol";symbol.textContent=t.symbol;symbol.setAttribute("aria-hidden","true");
    const label=document.createElement("strong");label.textContent=t.label;
    const note=document.createElement("span");note.className="workflow-use";note.textContent=t.use;
    b.append(symbol,label,note);
    b.addEventListener("click",()=>{
      if(selected.has(t.id))selected.delete(t.id);else selected.add(t.id);
      render();
    });
    choices.appendChild(b);
    buttons.set(t.id,b);
  }
  function render(){
    for(const [id,b] of buttons)b.setAttribute("aria-pressed",String(selected.has(id)));
    const picked=types.filter(t=>selected.has(t.id));
    summary.textContent=picked.length
      ? picked.length+" kind"+(picked.length===1?"":"s")+" of work selected. These are suggestions, not assignments."
      : "Choose one or more approaches to see a possible workflow.";
    steps.replaceChildren();
    if(!picked.length)return;
    const opening=document.createElement("li");
    const name=task.value.trim();
    opening.textContent=name
      ? "Define the outcome for “"+name+"” and the limits you want to respect."
      : "Name the task, the result you want, and any important limits.";
    steps.appendChild(opening);
    for(const t of picked){
      const li=document.createElement("li");
      const strong=document.createElement("strong");strong.textContent=t.label+" · ";
      li.append(strong,document.createTextNode(t.approach));
      steps.appendChild(li);
    }
    const review=document.createElement("li");
    review.textContent="Review what was actually done, what remains uncertain, and whether you want the next step.";
    steps.appendChild(review);
  }
  task.addEventListener("input",render);
  clear.addEventListener("click",()=>{selected.clear();task.value="";render();task.focus();});
  render();
})();
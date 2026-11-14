"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("index.html", "utf8");
const source = fs.readFileSync("link_choice.js", "utf8");
for (const id of ["open-choice-dialog","open-choice-tab","open-choice-window",
                  "open-choice-cancel","open-choice-destination"]) {
  assert(html.includes('id="' + id + '"'), "missing link choice " + id);
}
assert(!html.includes("View the portable Markdown Player Manual"),
       "redundant outdated manual link remains");
assert(html.includes('class="nav-external"'), "GitHub navigation entry missing");

function element(id) {
  return {id, textContent:"", handlers:{}, open:false,
    addEventListener(evt, handler){ this.handlers[evt] = handler; },
    click(){ this.handlers.click?.(); },
    showModal(){ this.open=true; },
    close(){ this.open=false; this.handlers.close?.(); }
  };
}
const ids = ["open-choice-dialog","open-choice-tab","open-choice-window",
             "open-choice-cancel","open-choice-destination"];
const els = Object.fromEntries(ids.map(id => [id,element(id)]));
const actions = [];
const document = {
  handlers:{},
  querySelector(selector){return els[selector.slice(1)] || null;},
  addEventListener(evt, fn){this.handlers[evt]=fn;}
};
const window = {
  location:{href:"http://127.0.0.1:8765/"},
  open:(url,target,features)=>actions.push({url,target,features})
};
vm.runInNewContext(source,{document,window,URL});
function clickLink(modifiers={}) {
  const link={href:"https://github.com/MedioCritasVT/CrystalCove",
              textContent:"CrystalCove on GitHub",hasAttribute:()=>false};
  let prevented=false;
  const event={defaultPrevented:false,button:0,ctrlKey:false,metaKey:false,
    altKey:false,shiftKey:false,target:{closest:()=>link},
    preventDefault:()=>{prevented=true;},...modifiers};
  document.handlers.click(event);
  return prevented;
}
assert.equal(clickLink(),true,"ordinary click should prompt");
assert(els["open-choice-dialog"].open,"dialog should open");
assert(els["open-choice-destination"].textContent.includes("github.com"));
els["open-choice-cancel"].click();
assert.equal(actions.length,0,"cancel must not launch");
assert.equal(els["open-choice-dialog"].open,false);

assert.equal(clickLink(),true);
els["open-choice-window"].click();
assert.equal(actions.length,1);
assert(actions[0].features.includes("popup=yes"),"window should request a distinct window");
assert.equal(actions[0].target,"_blank");

assert.equal(clickLink(),true);
els["open-choice-tab"].click();
assert.equal(actions.length,2);
assert(!actions[1].features.includes("popup=yes"),"tab must not request popup window");

assert.equal(clickLink({ctrlKey:true}),false,"Ctrl-click should keep normal browser behavior");
assert.equal(clickLink({button:1}),false,"middle-click should keep native behavior");
assert.equal(actions.length,2);
console.log("External links: tab/window/cancel, browser modifier bypass, GitHub nav, redundant manual OK");

"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("index.html","utf8");
for (const id of ["music-seek","music-elapsed","music-duration","music-visual-toggle",
  "music-visual-panel","music-visual-close","music-spectrum","music-visual-status"]) {
  assert(html.includes('id="'+id+'"'),"soundstage markup missing "+id);
}
class Element {
  constructor(id) {
    this.id=id; this.handlers={};this.attrs={};
    this.textContent="";this.value="0";this.disabled=true;this.hidden=false;
    this.duration=NaN;this.currentTime=0;this.paused=true;
  }
  addEventListener(evt,fn){const previous=this.handlers[evt];this.handlers[evt]=(event)=>{if(previous)previous(event);return fn(event);};}
  setAttribute(name,value){this.attrs[name]=value;}
  click(){return this.handlers.click?.();}
}
const ids=["music-audio","music-seek","music-elapsed","music-duration",
  "music-visual-toggle","music-visual-panel","music-visual-close",
  "music-visual-status","music-spectrum"];
const el=Object.fromEntries(ids.map(id=>[id,new Element(id)]));
el["music-visual-panel"].hidden=true;
const doc={hidden:false,handlers:{},
  querySelector(s){return el[s.slice(1)];},
  addEventListener(evt,fn){this.handlers[evt]=fn;}
};
let playCalls=0, frames=0;
el["music-audio"].play=()=>{playCalls++;};
const win={addEventListener(){},devicePixelRatio:1};
vm.runInNewContext(fs.readFileSync("soundstage.js","utf8"),{
  document:doc,window:win,Number,Math,Uint8Array,
  requestAnimationFrame:()=>++frames,cancelAnimationFrame:()=>{}
});
const audio=el["music-audio"],seek=el["music-seek"],clock=el["music-elapsed"];
assert.equal(seek.disabled,true,"unknown duration must disable seeking");
assert.equal(playCalls,0,"soundstage must not autoplay");
audio.duration=210;audio.currentTime=42;
audio.handlers.loadedmetadata();
assert.equal(seek.disabled,false);
assert.equal(el["music-duration"].textContent,"3:30");
assert.equal(clock.textContent,"0:42");
assert.equal(Number(seek.value),200);
seek.value="500";seek.handlers.input();
assert.equal(clock.textContent,"1:45");
seek.handlers.change();
assert.equal(audio.currentTime,105);
assert.equal(clock.textContent,"1:45");
el["music-visual-toggle"].click();
assert.equal(el["music-visual-panel"].hidden,false);
assert.equal(el["music-visual-toggle"].attrs["aria-expanded"],"true");
audio.paused=false;
audio.handlers.playing();
assert(el["music-visual-status"].textContent.includes("cannot capture"),"unsupported browser must fail visibly and safely");
el["music-visual-close"].click();
assert.equal(el["music-visual-panel"].hidden,true);
assert.equal(playCalls,0,"opening visualizer cannot start audio");
audio.duration=NaN;audio.handlers.emptied();
assert.equal(seek.disabled,true);
console.log("Soundstage: no autoplay, time display, seek commit, optional visualizer fallback and close OK");

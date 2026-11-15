"use strict";
// Review PRs belonging to the checkout's GitHub origin. Never merge on load.
(() => {
  const $=id=>document.getElementById(id);
  if(!$("pull-refresh"))return;
  let detail=null;
  let repository="";
  function notice(message,error=false){
    const e=$("pull-status");
    e.textContent=message;e.dataset.error=String(error);
  }
  function invalidate(){
    detail=null;
    $("pull-review").hidden=true;
    $("pull-merge").disabled=true;
    $("pull-open").hidden=true;
    $("pull-reviewed").checked=false;
  }
  async function read(path){
    const response=await fetch(path,{cache:"no-store"});
    const data=await response.json();
    if(!response.ok)throw Error(data.error||"Could not load GitHub data.");
    return data;
  }
  $("pull-refresh").addEventListener("click",async()=>{
    const button=$("pull-refresh");
    button.disabled=true;
    invalidate();
    $("pull-list").disabled=true;
    $("pull-inspect").disabled=true;
    $("pull-list").replaceChildren();
    notice("Loading GitHub pull requests…");
    try{
      const data=await read("/api/pulls/list");
      repository=data.repository;
      $("pull-repository").textContent="Repository: "+repository+
        (data.connected?" · signed-in GitHub App":" · public read-only");
      const blank=document.createElement("option");
      blank.value="";blank.textContent="Select a pull request";
      $("pull-list").append(blank);
      for(const pr of data.pulls){
        const option=document.createElement("option");
        option.value=String(pr.number);
        option.textContent="#"+pr.number+" · "+pr.title+(pr.draft?" (draft)":"");
        $("pull-list").append(option);
      }
      $("pull-list").disabled=data.pulls.length===0;
      notice(data.pulls.length+" open pull request(s) found"+
        (data.truncated?" (showing first 30).":"."));
    }catch(error){notice(error.message,true);}
    finally{button.disabled=false;}
  });
  $("pull-list").addEventListener("change",()=>{
    invalidate();
    $("pull-inspect").disabled=!$("pull-list").value;
  });
  $("pull-inspect").addEventListener("click",async()=>{
    const number=$("pull-list").value;
    if(!number)return;
    invalidate();
    $("pull-inspect").disabled=true;
    notice("Inspecting pull request #"+number+"…");
    try{
      detail=await read("/api/pulls/detail?number="+encodeURIComponent(number));
      $("pull-heading").textContent="#"+detail.number+" · "+detail.title;
      $("pull-meta").textContent=detail.repository+" · "+detail.base+
        " ← "+detail.head+" · "+detail.author+" · "+
        (detail.mergeable===true?"mergeable":detail.mergeable===false?"conflicting":"checks pending");
      $("pull-description").textContent=detail.body||"No description supplied.";
      const list=$("pull-files");
      list.replaceChildren();
      for(const item of detail.files){
        const row=document.createElement("section");
        row.className="pull-file";
        const heading=document.createElement("strong");
        heading.textContent=item.filename+" · +"+item.additions+" / -"+item.deletions;
        row.append(heading);
        if(item.patch){
          const patch=document.createElement("pre");
          patch.textContent=item.patch;
          patch.setAttribute("tabindex","0");
          row.append(patch);
        }
        list.append(row);
      }
      $("pull-warnings").textContent=detail.partial_file_list?
        "The full change could not be displayed safely here. Open the PR on GitHub to review or merge it.":
        "All returned text patches are shown. Confirm tests and required reviews before merging.";
      $("pull-review").hidden=false;
      const link=$("pull-open");
      link.href="https://github.com/"+repository+"/pull/"+detail.number+"/files";
      link.hidden=false;
      $("pull-reviewed").disabled=!detail.merge_available||!detail.review_complete;
      $("pull-merge").disabled=true;
      notice(detail.merge_available && detail.review_complete?
        "Review the changes, then explicitly confirm to merge.":
        "Viewing only: draft, missing permissions, pending checks, conflicts or incomplete diff.");
    }catch(error){notice(error.message,true);}
    finally{$("pull-inspect").disabled=false;}
  });
  $("pull-reviewed").addEventListener("change",()=>{
    $("pull-merge").disabled=!($("pull-reviewed").checked &&
      detail?.merge_available && detail?.review_complete);
  });
  $("pull-connect").addEventListener("click",()=>{
    document.getElementById("assistant-open-nav")?.click();
    notice("Use the GitHub connection in the assistant panel. A GitHub App must be configured first.");
  });
  $("pull-merge").addEventListener("click",async()=>{
    if(!detail?.merge_available || !detail?.review_complete || !$("pull-reviewed").checked)
      return;
    const phrase="MERGE #"+detail.number+" INTO "+detail.repository;
    const approval=window.prompt("GitHub merge authorization. Enter this exact text:\n"+phrase,"");
    if(approval!==phrase)return notice("Merge cancelled. Nothing changed.");
    const button=$("pull-merge");
    button.disabled=true;
    notice("Checking the current PR head with GitHub and requesting the approved merge…");
    try{
      const result=await post("/api/pulls/merge",{
        number:detail.number,sha:detail.head_sha,ticket:detail.ticket,
        merge_method:$("pull-method").value,confirmation:phrase
      });
      if(result.merged){
        invalidate();
        notice("GitHub confirmed the merge of #"+result.number+
          ". Update your checkout using the unchanged Check → Update → Relaunch controls above.");
      }
    }catch(error){notice(error.message,true);invalidate();}
  });
})();

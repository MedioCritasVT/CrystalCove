"use strict";
// A compact, opt-in soundstage: HTMLAudioElement seeking plus a real
// frequency analyzer when captureStream is supported. No microphone access,
// fake animation, audio uploading, or playback on page load.
(() => {
  const $ = s => document.querySelector(s);
  const audio = $("#music-audio");
  const seek = $("#music-seek");
  const elapsed = $("#music-elapsed");
  const total = $("#music-duration");
  const visualButton = $("#music-visual-toggle");
  const panel = $("#music-visual-panel");
  const visualClose = $("#music-visual-close");
  const visualStatus = $("#music-visual-status");
  const canvas = $("#music-spectrum");
  if (![audio,seek,elapsed,total,visualButton,panel,visualClose,visualStatus,canvas].every(Boolean)) return;

  const STEPS = 1000;
  let seeking = false;
  let context = null;
  let analyser = null;
  let freqData = null;
  let raf = 0;
  let nextFrame = 0;
  let capture = null;
  let connection = null;
  function duration() {
    return Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
  }
  function clock(value) {
    if (!Number.isFinite(value) || value < 0) return "0:00";
    const seconds = Math.floor(value);
    return Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2,"0");
  }
  function updateTime() {
    const len = duration();
    const current = Number.isFinite(audio.currentTime) ? audio.currentTime : 0;
    seek.disabled = !len;
    total.textContent = len ? clock(len) : "--:--";
    seek.setAttribute("aria-valuetext", clock(current) + (len ? " of " + clock(len) : " of unknown duration"));
    if (!seeking) {
      elapsed.textContent = clock(current);
      seek.value = len ? String(Math.max(0, Math.min(STEPS, Math.round(current / len * STEPS)))) : "0";
    }
  }
  seek.addEventListener("input", () => {
    if (!duration()) return;
    seeking = true;
    elapsed.textContent = clock(duration() * Number(seek.value) / STEPS);
  });
  seek.addEventListener("change", () => {
    if (duration()) {
      audio.currentTime = Math.min(duration(), Math.max(0, Number(seek.value) / STEPS * duration()));
    }
    seeking = false;
    updateTime();
  });
  for (const evt of ["timeupdate","durationchange","loadedmetadata","seeked","emptied"])
    audio.addEventListener(evt, updateTime);

  function showPanel(show) {
    panel.hidden = !show;
    visualButton.setAttribute("aria-expanded", String(show));
    if (show) {
      if (!audio.paused) void connect();
      else visualStatus.textContent = "Press Music On to see the real audio spectrum.";
    } else stopDrawing();
  }
  function stopDrawing() {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }
  function paint(now) {
    if (panel.hidden || !analyser || audio.paused) { stopDrawing(); return; }
    // Throttle redraw to ~30 FPS for a lightweight, unobtrusive visualizer.
    raf = requestAnimationFrame(paint);
    if (now - nextFrame < 33) return;
    nextFrame = now;
    analyser.getByteFrequencyData(freqData);
    const dpi = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(180, canvas.clientWidth || 300);
    const height = 112;
    if (canvas.width !== Math.floor(width*dpi) || canvas.height !== Math.floor(height*dpi)) {
      canvas.width = Math.floor(width*dpi);
      canvas.height = Math.floor(height*dpi);
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpi,0,0,dpi,0,0);
    ctx.clearRect(0,0,width,height);
    const bars = 32, gap = 3, cell = width/bars, barWidth = Math.max(2,cell-gap);
    const gradient = ctx.createLinearGradient(0,height,0,0);
    gradient.addColorStop(0,"#80d6bd");
    gradient.addColorStop(0.65,"#b9a9ef");
    gradient.addColorStop(1,"#e9bf84");
    ctx.fillStyle = gradient;
    for(let i=0;i<bars;i++) {
      // Gentle log-like mapping emphasizes bass without hiding higher notes.
      const bin = Math.min(freqData.length-1, Math.floor(Math.pow(i/(bars-1),1.55)*(freqData.length-1)));
      const value = (freqData[bin] || 0)/255;
      const h = Math.max(2,value*(height-10));
      ctx.fillRect(i*cell+gap/2,height-h,barWidth,h);
    }
  }
  async function connect() {
    if (panel.hidden || audio.paused) return;
    const Context = window.AudioContext || window.webkitAudioContext;
    const getStream = audio.captureStream || audio.mozCaptureStream;
    if (!Context || !getStream) {
      visualStatus.textContent = "This browser cannot capture the audio spectrum. Playback and seeking still work.";
      return;
    }
    try {
      if (!context) context = new Context();
      if (context.state === "suspended") await context.resume();
      if (!analyser) {
        capture = getStream.call(audio);
        // A MediaStreamSource reads a copy of the playing audio. We never
        // reroute the original audio element, so playback is unaffected.
        if (!capture.getAudioTracks().length)
          throw Error("Waiting for an audio track");
        connection = context.createMediaStreamSource(capture);
        analyser = context.createAnalyser();
        analyser.fftSize = 512;
        analyser.smoothingTimeConstant = .75;
        connection.connect(analyser);
        freqData = new Uint8Array(analyser.frequencyBinCount);
      }
      visualStatus.textContent = "Live spectrum · read-only audio, no microphone.";
      stopDrawing();
      raf = requestAnimationFrame(paint);
    } catch {
      visualStatus.textContent = "Live spectrum is unavailable for this track or browser. Audio will continue normally.";
    }
  }
  visualButton.addEventListener("click", () => showPanel(panel.hidden));
  visualClose.addEventListener("click", () => showPanel(false));
  audio.addEventListener("playing", () => {if (!panel.hidden) void connect();});
  audio.addEventListener("pause", stopDrawing);
  audio.addEventListener("emptied", () => {
    // New track can replace the stream: disconnect the old analyzer cleanly.
    stopDrawing();
    if (connection) connection.disconnect();
    connection = null;
    analyser = null;
    capture = null;
    visualStatus.textContent = "Waiting for playback.";
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopDrawing();
    else if (!panel.hidden && !audio.paused) void connect();
  });
  window.addEventListener("beforeunload", () => {
    stopDrawing();
    if (connection) connection.disconnect();
    if (context) void context.close();
  });
  updateTime();
})();

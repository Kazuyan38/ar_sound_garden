/*
 * audio-loader.js
 * AudioContext + 5音源プリロード + BPM同期再生マネージャ
 * window.AudioManager にシングルトンを公開
 */
(function () {
  "use strict";

  const TRACKS = [
    { id: "drum",   url: "assets/audio/drum_loop.wav"   },
    { id: "bass",   url: "assets/audio/bass_loop.wav"   },
    { id: "melody", url: "assets/audio/melody_loop.wav" },
    { id: "pad",    url: "assets/audio/pad_loop.wav"    },
    { id: "arp",    url: "assets/audio/arp_loop.wav"    },
  ];

  const AudioManager = {
    ctx: null,
    buffers: {},
    sources: {},
    panners: {},
    gains: {},
    ready: false,
    startTime: 0,
    _readyResolvers: [],

    async start() {
      if (this.ctx) return;
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (this.ctx.state === "suspended") {
        await this.ctx.resume();
      }
      await Promise.all(TRACKS.map((t) => this._loadTrack(t)));
      this._scheduleSyncStart();
      this.ready = true;
      this._readyResolvers.forEach((r) => r());
      this._readyResolvers = [];
      console.log("[AudioManager] ready, sync started at", this.startTime.toFixed(3));
    },

    onReady(cb) {
      if (this.ready) {
        cb();
      } else {
        this._readyResolvers.push(cb);
      }
    },

    async _loadTrack(track) {
      const res = await fetch(track.url);
      const ab = await res.arrayBuffer();
      this.buffers[track.id] = await this.ctx.decodeAudioData(ab);
      console.log(`[AudioManager] loaded ${track.id} (${this.buffers[track.id].duration.toFixed(2)}s)`);
    },

    _scheduleSyncStart() {
      this.startTime = this.ctx.currentTime + 0.25;
      TRACKS.forEach((t) => {
        const src = this.ctx.createBufferSource();
        src.buffer = this.buffers[t.id];
        src.loop = true;

        const panner = this.ctx.createPanner();
        panner.panningModel = "HRTF";
        panner.distanceModel = "inverse";
        panner.refDistance = 1.0;
        panner.maxDistance = 20.0;
        panner.rolloffFactor = 1.8;
        panner.coneInnerAngle = 360;

        const gain = this.ctx.createGain();
        gain.gain.value = 0.85;

        src.connect(panner).connect(gain).connect(this.ctx.destination);
        src.start(this.startTime);

        this.sources[t.id] = src;
        this.panners[t.id] = panner;
        this.gains[t.id] = gain;
      });
    },

    setPanner(id, x, y, z) {
      const p = this.panners[id];
      if (!p) return;
      if (p.positionX) {
        p.positionX.value = x;
        p.positionY.value = y;
        p.positionZ.value = z;
      } else {
        p.setPosition(x, y, z);
      }
    },

    setListener(pos, forward, up) {
      if (!this.ctx) return;
      const L = this.ctx.listener;
      if (L.positionX) {
        L.positionX.value = pos.x;
        L.positionY.value = pos.y;
        L.positionZ.value = pos.z;
        L.forwardX.value = forward.x;
        L.forwardY.value = forward.y;
        L.forwardZ.value = forward.z;
        L.upX.value = up.x;
        L.upY.value = up.y;
        L.upZ.value = up.z;
      } else {
        L.setPosition(pos.x, pos.y, pos.z);
        L.setOrientation(forward.x, forward.y, forward.z, up.x, up.y, up.z);
      }
    },

    bpm: 128,
    secPerBeat() {
      return 60.0 / this.bpm;
    },
    currentBeat() {
      if (!this.ctx || !this.ready) return 0;
      return (this.ctx.currentTime - this.startTime) / this.secPerBeat();
    },
    beatPhase() {
      const b = this.currentBeat();
      return b - Math.floor(b);
    },
  };

  window.AudioManager = AudioManager;
})();

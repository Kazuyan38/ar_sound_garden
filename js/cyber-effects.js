/*
 * cyber-effects.js
 * A-Frame components:
 *   - beat-pulse: scales the entity in sync with the 128 BPM beat
 *   - slow-spin: continuous rotation
 *   - neon-bloom: post-processing-free pseudo-bloom via emissive overshoot
 *   - particle-aura: small particle cloud orbiting the object
 */
(function () {
  "use strict";

  if (typeof AFRAME === "undefined") {
    console.error("[cyber-effects] AFRAME not loaded");
    return;
  }

  AFRAME.registerComponent("beat-pulse", {
    schema: {
      multiplier:  { type: "number", default: 1.0 },
      strength:    { type: "number", default: 0.18 },
      baseScale:   { type: "number", default: 1.0 },
    },
    tick: function () {
      const am = window.AudioManager;
      if (!am || !am.ready) {
        this.el.object3D.scale.setScalar(this.data.baseScale);
        return;
      }
      const phase = (am.currentBeat() * this.data.multiplier) % 1.0;
      const decay = Math.exp(-phase * 6.0);
      const s = this.data.baseScale * (1.0 + this.data.strength * decay);
      this.el.object3D.scale.setScalar(s);
    },
  });

  AFRAME.registerComponent("slow-spin", {
    schema: {
      axis:  { type: "vec3",   default: { x: 0, y: 1, z: 0 } },
      speed: { type: "number", default: 0.3 },
    },
    tick: function (t, dt) {
      const rad = (dt / 1000) * this.data.speed * Math.PI * 2;
      const ax = this.data.axis;
      this.el.object3D.rotateOnAxis(new THREE.Vector3(ax.x, ax.y, ax.z).normalize(), rad);
    },
  });

  AFRAME.registerComponent("neon-bloom", {
    schema: {
      color:     { type: "color",  default: "#ff10f0" },
      intensity: { type: "number", default: 2.0 },
      pulse:     { type: "number", default: 0.6 },
    },
    init: function () {
      this.el.addEventListener("model-loaded", () => this._apply());
      this._apply();
    },
    _apply: function () {
      const mesh = this.el.getObject3D("mesh");
      if (!mesh) return;
      mesh.traverse((node) => {
        if (node.isMesh && node.material) {
          const c = new THREE.Color(this.data.color);
          node.material.color = c.clone().multiplyScalar(0.4);
          node.material.emissive = c;
          node.material.emissiveIntensity = this.data.intensity;
          node.material.toneMapped = false;
          node.material.needsUpdate = true;
        }
      });
    },
    tick: function () {
      const mesh = this.el.getObject3D("mesh");
      if (!mesh) return;
      const am = window.AudioManager;
      if (!am || !am.ready) return;
      const phase = am.currentBeat() % 1.0;
      const decay = Math.exp(-phase * 5.0);
      const ei = this.data.intensity * (1.0 + this.data.pulse * decay);
      mesh.traverse((node) => {
        if (node.isMesh && node.material) node.material.emissiveIntensity = ei;
      });
    },
  });

  AFRAME.registerComponent("particle-aura", {
    schema: {
      color:  { type: "color",  default: "#ff10f0" },
      count:  { type: "number", default: 60 },
      radius: { type: "number", default: 0.6 },
      size:   { type: "number", default: 0.025 },
      speed:  { type: "number", default: 0.4 },
    },
    init: function () {
      const n = this.data.count;
      const positions = new Float32Array(n * 3);
      const phases    = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        phases[i] = Math.random() * Math.PI * 2;
        positions[i*3]   = 0;
        positions[i*3+1] = 0;
        positions[i*3+2] = 0;
      }
      const geom = new THREE.BufferGeometry();
      geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const mat = new THREE.PointsMaterial({
        color: new THREE.Color(this.data.color),
        size: this.data.size,
        transparent: true,
        opacity: 0.9,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true,
      });
      this._points = new THREE.Points(geom, mat);
      this.el.object3D.add(this._points);
      this._phases = phases;
      this._t = 0;
    },
    tick: function (t, dt) {
      this._t += (dt / 1000) * this.data.speed;
      const pos = this._points.geometry.attributes.position.array;
      const r = this.data.radius;
      for (let i = 0; i < this.data.count; i++) {
        const ph = this._phases[i] + this._t * (1.0 + (i % 7) * 0.05);
        const yPh = ph * 0.7 + i * 0.3;
        pos[i*3]   = Math.cos(ph) * r * (0.6 + 0.4 * Math.sin(ph * 1.7));
        pos[i*3+1] = Math.sin(yPh * 1.3) * r * 0.8;
        pos[i*3+2] = Math.sin(ph) * r * (0.6 + 0.4 * Math.cos(ph * 1.7));
      }
      this._points.geometry.attributes.position.needsUpdate = true;
    },
  });

  AFRAME.registerComponent("grid-floor", {
    schema: {
      size:     { type: "number", default: 20 },
      divisions:{ type: "number", default: 40 },
      color1:   { type: "color",  default: "#ff10f0" },
      color2:   { type: "color",  default: "#00ffff" },
    },
    init: function () {
      const grid = new THREE.GridHelper(this.data.size, this.data.divisions, this.data.color1, this.data.color2);
      grid.material.transparent = true;
      grid.material.opacity = 0.35;
      grid.material.depthWrite = false;
      grid.position.y = 0;
      this.el.object3D.add(grid);
    },
  });
})();

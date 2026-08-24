/*
 * spatial-audio.js
 * A-Frame components:
 *   - audio-listener: place on camera, updates Web Audio listener every frame
 *   - spatial-audio-source: place on each sound object, updates its PannerNode position
 */
(function () {
  "use strict";

  if (typeof AFRAME === "undefined") {
    console.error("[spatial-audio] AFRAME not loaded");
    return;
  }

  const tmpV1 = new THREE.Vector3();
  const tmpV2 = new THREE.Vector3();
  const tmpV3 = new THREE.Vector3();
  const tmpQ  = new THREE.Quaternion();

  AFRAME.registerComponent("audio-listener", {
    tick: function () {
      const am = window.AudioManager;
      if (!am || !am.ready) return;
      const obj = this.el.object3D;
      obj.updateMatrixWorld();
      tmpV1.setFromMatrixPosition(obj.matrixWorld);
      obj.getWorldQuaternion(tmpQ);
      tmpV2.set(0, 0, -1).applyQuaternion(tmpQ);
      tmpV3.set(0, 1, 0).applyQuaternion(tmpQ);
      am.setListener(tmpV1, tmpV2, tmpV3);
    },
  });

  AFRAME.registerComponent("spatial-audio-source", {
    schema: {
      track: { type: "string", default: "" },
    },
    tick: function () {
      const am = window.AudioManager;
      if (!am || !am.ready) return;
      const obj = this.el.object3D;
      obj.updateMatrixWorld();
      tmpV1.setFromMatrixPosition(obj.matrixWorld);
      am.setPanner(this.data.track, tmpV1.x, tmpV1.y, tmpV1.z);
    },
  });
})();

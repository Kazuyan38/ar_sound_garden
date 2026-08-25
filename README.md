# AR Sound Garden

**公開URL: https://kazuyan38.github.io/ar_sound_garden/**

サイバーポップEDM美学のインタラクティブWebAR作品。スマホでURLを開くと、現実空間に5体の発光オブジェクトが浮かび、各々が128 BPM同期で異なる音楽パート（ドラム / ベース / メロディ / パッド / アルペジオ）をループ再生する。あなたが歩き回ると距離と方向に応じて音量・定位が変化し、自分だけのリミックスが生まれる。

## クイックスタート（ローカル確認）

```sh
cd C:\Users\gener\ar_sound_garden
python -m http.server 8000
```

ブラウザで http://localhost:8000/ を開いて「TAP TO ENTER」をクリック。デスクトップではマウスドラッグで視点操作、`W/A/S/D` で移動できる。

### スマホ実機で確認するには

WebXR ARは **HTTPS** 必須なので、`localhost` 以外で動かすにはHTTPS環境が必要。最も簡単なのは GitHub Pages にデプロイすること。手順は [DEPLOY.md](DEPLOY.md) を見て。

開発中だけ実機で見たい場合は ngrok などのトンネルを使う:
```sh
ngrok http 8000
```
表示された `https://xxxx.ngrok-free.app` をスマホで開く。

## 対応環境

| 環境 | 動作モード | 体験 |
|---|---|---|
| **Android Chrome** | WebXR本格AR（6DoF） | 部屋の中を物理的に歩き回って体験 |
| **iPhone Safari (13+)** | カメラ＋ジャイロ疑似AR（3DoF） | カメラ映像の上にオブジェクトが浮かぶ。スマホ回転で見回せる |
| デスクトップ Chrome | 3Dプレビュー | マウスドラッグで視点回転 / W,A,S,Dで移動 |
| デスクトップ Firefox/Safari | 3Dプレビュー | 同上 |

### iPhoneとAndroidの違い

iPhone Safariは現状WebXRをサポートしていないため、本格6DoF AR（物理的に動き回れる）はAndroid Chromeのみ。**iPhoneでは「カメラを背景に流し、ジャイロでカメラ回転」する疑似ARモード** を自動で起動する。物理的に歩き回ることはできないが、スマホを360度回すと音と映像の方向感が変化するため、AR音庭園のコアな体験は成立する。

### 初回タップ時の許可ダイアログ

- **iPhone**: 「動きの検知」「カメラ」の2つの許可が求められる → 両方とも「許可」を選ぶ
- **Android**: 「カメラ」の許可のみ（ARモード起動時にARCoreが自動で動きの検知を行う）

## プロジェクト構成

```
ar_sound_garden/
├── index.html               # メインARシーン
├── js/
│   ├── audio-loader.js      # AudioContext + 5音源ロード + 同期再生
│   ├── spatial-audio.js     # PannerNode による3D空間音響
│   └── cyber-effects.js     # ネオン発光・ビートパルス・パーティクル
├── assets/
│   └── audio/               # 5本のループWAV（128 BPM, 15.000秒）
└── audio_gen/
    └── generate_loops.py    # 音源再生成スクリプト（依存: numpy のみ）
```

## カスタマイズ

### 自分の音源に差し替える
`assets/audio/` の5本のWAVを差し替えるだけ。条件：
- 全ファイルの長さを **完全に同じ** にする（128 BPM で 15.000s = 8小節がデフォルト）
- 異なるBPMにしたい場合は `js/audio-loader.js` の `bpm: 128` と `js/cyber-effects.js` の `beat-pulse` 系の値も連動して変更
- ファイル名は維持（`drum_loop.wav` 等）。変えたい場合は `js/audio-loader.js` の `TRACKS` 配列も同期して変更

### 音源を再生成する（プログラマブル音楽）
```sh
python audio_gen/generate_loops.py
```
コードパターンやコード進行は `audio_gen/generate_loops.py` の `CHORDS` 配列と各 `make_*()` 関数を編集すると変えられる。今のデフォルトは Am - F - C - G の8小節。

### 3Dオブジェクトの形と色を変える
`index.html` の各 `<a-box>`, `<a-sphere>` 等のタグを編集:
- `position="x y z"` で配置を変える
- `neon-bloom="color: #xxxxxx; intensity: 数値"` で発光色・強さ
- `beat-pulse="multiplier: 数値; strength: 数値"` でビート同期の挙動
  - `multiplier=0.5` → 2拍に1回パルス
  - `multiplier=4.0` → 1拍に4回パルス（16分音符）
- `particle-aura` パラメータでオーラの広がり・粒子数

### Blender製の高品質モデルに置き換えたい
A-Frameは glTF を直接読み込める。各プリミティブを以下に置き換える:
```html
<a-entity gltf-model="assets/models/drum_cube.glb" position="0 0.7 -1.8"
          neon-bloom="..." beat-pulse="..." spatial-audio-source="track: drum"></a-entity>
```
glTFエクスポート時は **Apply Modifiers ON / Y-Up / Materials ON** にする。

## デプロイ

GitHub Pages で公開する手順は [DEPLOY.md](DEPLOY.md) を参照。

## 技術スタック

- **A-Frame 1.5** — HTML的に書ける3D/AR/VRフレームワーク
- **Web Audio API** — `PannerNode` (HRTF) で3D空間音響、`AudioBufferSourceNode` で同期ループ再生
- **WebXR Device API** — ARモード起動（Android Chrome ネイティブサポート）
- **Three.js** — A-Frameが内部で使用。`neon-bloom` 等のシェーダ操作で使う
- **Python + numpy** — 音源プログラム生成（SoundFontなしの直接波形合成）

## 既知の制約

- iOS Safari は WebXR が制限的。動くがARモード起動はしないケースあり
- スマホによってはWebAudioの初回起動でタップが2回必要なことがある
- 自宅 Wi-Fi 内で実機テストするには HTTPS が必須（ngrok か GitHub Pages）

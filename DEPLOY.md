# Deploy to GitHub Pages

WebXR AR は HTTPS 必須。最速の無料公開方法は GitHub Pages。所要 約10分。

## 前提

- GitHub アカウントがある
- ローカルに git がインストール済み

確認:
```sh
git --version
```

## ステップ 1: GitHub にリポジトリを作る

1. https://github.com/new を開く
2. Repository name: `ar-sound-garden`（好きな名前でOK）
3. Public を選択（GitHub Pages 無料プランは Public のみ）
4. **Initialize this repository は何もチェックしない**
5. 「Create repository」

## ステップ 2: ローカルからプッシュ

```sh
cd C:\Users\gener\ar_sound_garden
git init
git add .
git commit -m "Initial commit: AR Sound Garden"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/ar-sound-garden.git
git push -u origin main
```

`<YOUR_USERNAME>` は自分のGitHubユーザー名に置き換える。

## ステップ 3: GitHub Pages を有効化

1. リポジトリページ → **Settings** タブ
2. 左サイドバーの **Pages**
3. **Source** で **Deploy from a branch** を選択
4. **Branch** で `main` / `/(root)` を選んで **Save**
5. 数分待つ（最初のデプロイは1〜3分かかる）

公開URL:
```
https://<YOUR_USERNAME>.github.io/ar-sound-garden/
```

## ステップ 4: スマホで確認

### Android Chromeの場合（本格AR）

1. Chrome で URL を開く
2. 「TAP TO ENTER」をタップ
3. カメラ許可 → 許可
4. WebXR ARモードに入る → 部屋に5体のオブジェクトが浮かぶ
5. 物理的に歩き回って音が変化することを確認

### iPhone Safariの場合（疑似AR）

1. Safari で URL を開く（**Chrome iOS版ではなく Safari** が必要）
2. 「TAP TO ENTER」をタップ
3. 「動きの検知」許可ダイアログ → 許可
4. 「カメラ」許可ダイアログ → 許可
5. カメラ映像が背景に流れ、5体のオブジェクトが浮かぶ
6. スマホを360度回して音の方向感が変わることを確認

iPhoneでは物理移動はトラッキングされないが、スマホの向きに応じて音と視点が変化する。

## トラブルシューティング

### 「サイトにアクセスできません」が出る
GitHub Pages のビルド待ち。1〜3分待ってリロード。Settings → Pages のページに「Your site is live at ...」が出ているか確認。

### 「TAP TO ENTER」を押しても何も起こらない
ブラウザの開発者ツール（Chrome なら `chrome://inspect` 経由）でコンソールエラーを確認。よくある原因:
- 音源ファイルが404 → コミット漏れ。`git status` で `assets/audio/` 配下のwavがコミット済みか確認
- HTTPS でアクセスしているか確認（URLが `https://` で始まっている）

### Android: AR モードに入れない
- Android Chrome を最新版に更新
- ARCore 対応端末か確認（[対応リスト](https://developers.google.com/ar/devices)）
- 「Google Play for AR」をインストール（初回は自動プロンプト）

### iPhone: カメラが映らない・回転しても何も変わらない
- iOS Safari で開いているか確認（Chrome iOS は WebKitベースだが許可周りで問題が出ることあり）
- 「設定 → Safari → モーションと画面の向きへのアクセス」がオンになっているか確認
- ページをリロードして許可ダイアログをやり直す
- iOS 13未満の場合は動作しない（iOS 13+で動作確認済み）

### 音が出ない
- スマホのマナーモードを解除
- スマホのメディア音量を上げる
- 一度「TAP TO ENTER」前に画面を1回タップしてから本番タップする（一部端末で必要）

## 自分の音楽に差し替える

1. `assets/audio/` の5本のWAVを自作音源で置き換え（同じファイル名・長さで）
2. コミットしてプッシュ
   ```sh
   git add assets/audio/
   git commit -m "Replace audio with custom mix"
   git push
   ```
3. GitHub Pages が自動で再ビルド（1〜2分）

## QRコード化して配布する（任意）

公開URLをQRコードにすると、ライブやポスターでの配布が容易。
- https://www.qr-code-generator.com/ などで URL を入力するだけ
- 印刷物・SNS画像に埋め込んで「カメラかざすだけで体験できるAR音楽作品」として配布可能

## カスタムドメインを使う（任意）

GitHub Pages は無料カスタムドメインに対応。Settings → Pages → Custom domain で設定可能。Let's Encrypt SSL自動付与。

---

公開後、URLを共有すれば誰でも・どこからでも・アプリ不要で体験できる。

# Flight Cheap CLI - 実装計画

## 概要
航空券を安く取得するための7つの分析プロンプトを提供し、Playwright（Google Flights）から取得した実データと Claude Code による対話的な分析を組み合わせて、包括的な価格最適化レポートを提供するPython CLIツール。

## 技術スタック
- 言語: Python 3.11+
- データ取得: Playwright (Chromium headless browser)
- 分析: Claude Code 対話セッション（API不要）
- CLI: click
- 出力整形: rich
- 環境変数: python-dotenv
- テスト: pytest（51テスト）

## 開発アプローチ
**TDD（Test-Driven Development）で進める**
- 各モジュール実装時に、先にテストを書いてから実装
- テストファイル: `tests/test_fetcher.py`, `tests/test_prompts.py` など
- Mock/Stub: 外部依存はモックして排除
- 段階的に機能を追加し、テストが常に緑を保つようにする

## ディレクトリ構造
```
flight_cheap/
├── src/
│   ├── __init__.py
│   ├── cli.py           # メインエントリポイント、引数解析
│   ├── fetcher.py       # Playwright連携、フライトデータ取得
│   ├── prompts.py       # 7つのプロンプト定義（参考用）
│   └── formatter.py     # ターミナル出力整形（rich使用）
├── tests/
│   ├── __init__.py
│   ├── test_fetcher.py       # fetcher.pyのテスト
│   ├── test_prompts.py       # prompts.pyのテスト
│   ├── test_formatter.py     # formatter.pyのテスト
│   ├── test_cli.py           # cli.pyのテスト
│   └── test_dependencies.py  # 依存関係検証
├── .env.example         # 環境変数テンプレート
├── pytest.ini           # pytest設定
├── pyproject.toml       # 依存関係・プロジェクト設定
└── spec.md              # 既存
```

## 実装ステップ（全完了）

### Step 1: プロジェクト基盤セットアップ ✓
- [x] pyproject.toml作成（依存関係定義）
- [x] .env.example作成
- [x] src/__init__.py作成

### Step 2: prompts.py実装 ✓
- [x] spec.mdから7つのプロンプトを読み込み
- [x] Claude Code 対話用のフォーマットに変換

### Step 3: fetcher.py実装 ✓
- [x] Playwright クライアント初期化
- [x] Google Flights スクレイピング関数
- [x] 近隣空港検索オプション

### Step 4: formatter.py実装 ✓
- [x] richを使った出力整形
- [x] セクション分け、テーブル表示
- [x] サマリー生成

### Step 5: cli.py実装 ✓
- [x] clickによる引数解析
- [x] 全体フローの統合
- [x] エラーハンドリング
- [x] Claude Code 対話ワークフロー案内

### Step 6: 動作確認 ✓
- [x] 実際のルートで検索テスト
- [x] 出力確認

### Step 7: Headless Browser Migration (2026-01-14完了) ✓
- [x] SerpAPI依存の削除
- [x] Gemini API依存の削除
- [x] Playwright実装
- [x] Claude Code対話ワークフローへの移行
- [x] テスト更新（51テスト全パス）
- [x] ドキュメント更新（README.md, .env.example）

## CLIインターフェース
```bash
# 基本
flight-cheap search --from TYO --to LAX --date 2025-03-01

# 往復
flight-cheap search --from TYO --to LAX --date 2025-03-01 --return 2025-03-15

# 近隣空港含む
flight-cheap search --from TYO --to LAX --date 2025-03-01 --nearby
```

## 環境変数
```
# オプション設定のみ（API鍵不要）
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=3
```

## 検証方法
1. `pip install -e .` でローカルインストール
2. `playwright install chromium` でブラウザインストール
3. `flight-cheap search --from TYO --to LAX --date 2025-03-15` を実行
4. フライトデータが取得され、JSONファイルに保存される
5. Claude Code で対話的に分析

## 最終検証ステップ（2026-01-14実施）✓

### 依存関係の検証
- [x] pyproject.tomlにplaywrightが含まれる
- [x] pyproject.tomlからserpapi削除済み
- [x] pyproject.tomlからgoogle-generativeai削除済み
- [x] .env.exampleからSERPAPI_KEY削除済み
- [x] .env.exampleからGEMINI_API_KEY削除済み
- [x] .env.exampleにPlaywrightインストール手順を追加

### ドキュメントの検証
- [x] README.mdからSerpAPI参照削除済み
- [x] README.mdからGemini API参照削除済み
- [x] README.mdにPlaywrightセットアップ手順を追加
- [x] README.mdにClaude Code対話ワークフロー説明を追加

### テストの検証
- [x] 全51テストがパス
- [x] test_dependencies.pyに検証テスト追加（12テスト）
- [x] test_cli.pyにクリーンアップ検証（2テスト）

### マイグレーション完了
**Migration Status: ✓ COMPLETED**
- API依存ゼロ（コスト削減）
- Playwright headless browserで安定動作
- Claude Code対話で柔軟な分析
- 全テストパス（51/51）
- ドキュメント完全更新

**最終更新:** 2026-01-14

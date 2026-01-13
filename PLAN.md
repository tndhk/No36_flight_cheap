# Flight Cheap CLI - 実装計画

## 概要
航空券を安く取得するための7つの分析プロンプトを実行し、SerpAPI（Google Flights）から取得した実データとGemini APIによる分析を組み合わせて、包括的な価格最適化レポートを出力するPython CLIツール。

## 技術スタック
- 言語: Python 3.11+
- データ取得: SerpAPI（Google Flights）
- LLM: Gemini API（google-generativeai）
- CLI: click
- 出力整形: rich
- 環境変数: python-dotenv
- 非同期: asyncio（3並列制限）
- テスト: pytest, unittest.mock（テスト駆動開発）

## 開発アプローチ
**TDD（Test-Driven Development）で進める**
- 各モジュール実装時に、先にテストを書いてから実装
- テストファイル: `tests/test_fetcher.py`, `tests/test_analyzer.py` など
- Mock/Stub: SerpAPI、Gemini APIはモックして外部依存を排除
- 段階的に機能を追加し、テストが常に緑を保つようにする

## ディレクトリ構造
```
flight_cheap/
├── src/
│   ├── __init__.py
│   ├── cli.py           # メインエントリポイント、引数解析
│   ├── fetcher.py       # SerpAPI連携、フライトデータ取得
│   ├── analyzer.py      # Gemini API連携、非同期プロンプト実行
│   ├── prompts.py       # 7つのプロンプト定義
│   └── formatter.py     # ターミナル出力整形（rich使用）
├── tests/
│   ├── __init__.py
│   ├── test_fetcher.py       # fetcher.pyのテスト
│   ├── test_analyzer.py      # analyzer.pyのテスト
│   ├── test_prompts.py       # prompts.pyのテスト
│   ├── test_formatter.py     # formatter.pyのテスト
│   └── test_cli.py           # cli.pyのテスト
├── .env.example         # API鍵テンプレート
├── pytest.ini           # pytest設定
├── pyproject.toml       # 依存関係・プロジェクト設定
└── spec.md              # 既存
```

## 実装ステップ

### Step 1: プロジェクト基盤セットアップ
- [ ] pyproject.toml作成（依存関係定義）
- [ ] .env.example作成
- [ ] src/__init__.py作成

### Step 2: prompts.py実装
- [ ] spec.mdから7つのプロンプトを読み込み
- [ ] フライトデータを埋め込むためのテンプレート形式に変換

### Step 3: fetcher.py実装
- [ ] SerpAPIクライアント初期化
- [ ] Google Flights検索関数
- [ ] 近隣空港検索オプション

### Step 4: analyzer.py実装
- [ ] Geminiクライアント初期化
- [ ] 非同期プロンプト実行（asyncio.Semaphoreで3並列制限）
- [ ] asyncio.gatherで7つの分析を並列実行

### Step 5: formatter.py実装
- [ ] richを使った出力整形
- [ ] セクション分け、テーブル表示
- [ ] サマリー生成

### Step 6: cli.py実装
- [ ] clickによる引数解析
- [ ] 全体フローの統合
- [ ] エラーハンドリング

### Step 7: 動作確認
- [ ] 実際のルートで検索テスト
- [ ] 出力確認

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
SERPAPI_KEY=your_serpapi_key
GEMINI_API_KEY=your_gemini_key
```

## 検証方法
1. `pip install -e .` でローカルインストール
2. `.env`ファイルにAPI鍵を設定
3. `flight-cheap search --from TYO --to LAX --date 2025-03-15` を実行
4. 7つの分析結果がターミナルに表示されることを確認

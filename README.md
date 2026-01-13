# Flight Cheap CLI

航空券を安く取得するための AI 分析ツール。Google Flights のデータを Playwright でスクレイピングし、Claude Code による対話的な分析で価格最適化戦略を提案します。

## 機能

**Claude Code 対話分析ワークフロー:**

Google Flights のフライトデータを取得後、Claude Code との対話的なセッションで以下のような分析が可能です:

1. **Hidden Route Scanner** - 隠れたルートを発見（経由地、近隣空港の組み合わせ）
2. **Price Manipulation Detector** - 価格操作を検出（最適検索方法を提案）
3. **Geo-Pricing Bypass** - 地域別価格を比較（最安地域を特定）
4. **Timing Sweet Spot Finder** - 最適な予約タイミング（需要サイクルを分析）
5. **Fare Rule Exploiter** - 運賃ルールを分析（ルール外の節約法）
6. **Airline VS OTA Comparison** - 航空会社と OTA を比較（最安プラットフォーム特定）
7. **Price Drop Watch Strategy** - 価格追跡戦略（監視方法を詳細化）

## セットアップ

### 前提条件

- Python 3.11 以上
- Git
- Claude Code CLI (推奨)

### 1. リポジトリをクローン

```bash
git clone https://github.com/tndhk/No36_flight_cheap.git
cd No36_flight_cheap
```

### 2. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係をインストール

```bash
pip install -e .
```

### 4. Playwright ブラウザをインストール

```bash
playwright install chromium
```

このコマンドで Chromium ブラウザがダウンロードされます（約 150MB）。

### 5. 環境変数を設定（オプション）

```bash
cp .env.example .env
```

`.env` ファイルでログレベルなどを調整できます（API キーは不要）。

## 使用方法

### 基本的な検索

```bash
flight-cheap search --from TYO --to LAX --date 2025-03-01
```

### 往復便

```bash
flight-cheap search --from TYO --to LAX --date 2025-03-01 --return 2025-03-15
```

### 近隣空港も含める

```bash
flight-cheap search --from TYO --to LAX --date 2025-03-01 --nearby
```

### Claude Code で対話的分析

データ取得後、Claude Code との対話セッションが開始されます。以下のような質問で分析を依頼できます:

```
「このルートで最安の組み合わせを教えて」
「価格変動の傾向を分析して」
「経由地を使った節約方法は?」
「いつ予約するのが最適?」
```

### ヘルプ表示

```bash
flight-cheap search --help
```

## 出力例

```
Flight Cheap CLI
============================================================
Search: TYO → LAX (2025-03-01)

Fetching flight data from Google Flights...
Found 15 flights

Saving data to: /path/to/flight_data_TYO-LAX_2025-03-01.json

============================================================
Flight data saved. You can now analyze it with Claude Code:

  claude code chat

Then ask questions like:
  - "Analyze the flight data in flight_data_TYO-LAX_2025-03-01.json"
  - "What's the cheapest route combination?"
  - "When is the best time to book?"

============================================================
```

## プロジェクト構成

```
flight_cheap/
├── src/
│   ├── __init__.py
│   ├── prompts.py      # 7つの分析プロンプト定義（参考用）
│   ├── fetcher.py      # Playwright スクレイピング
│   ├── formatter.py    # 出力整形 (Rich ライブラリ)
│   └── cli.py          # Click CLI メイン
├── tests/
│   ├── test_prompts.py       # 16 テスト
│   ├── test_fetcher.py       # 13 テスト
│   ├── test_formatter.py     # 9 テスト
│   ├── test_cli.py           # 10 テスト
│   └── test_dependencies.py  # 依存関係検証
├── .env.example        # 環境変数テンプレート
├── .gitignore
├── pyproject.toml      # 依存関係 + プロジェクト設定
├── pytest.ini          # pytest 設定
└── README.md           # このファイル
```

## 技術スタック

- **言語:** Python 3.11+
- **Data Fetching:** Playwright (Chromium headless browser)
- **分析:** Claude Code 対話セッション
- **CLI:** Click
- **出力整形:** Rich
- **テスト:** pytest (48 テスト)

## 開発者向け情報

### テスト実行

全テストを実行:

```bash
pytest tests/ -v
```

特定のテストのみ:

```bash
pytest tests/test_prompts.py -v
```

### 開発環境セットアップ

```bash
pip install -e ".[dev]"
```

このコマンドで以下が追加インストールされます:
- pytest
- pytest-cov
- pytest-asyncio
- black
- isort
- mypy
- ruff

### コード整形

```bash
black src/ tests/
isort src/ tests/
```

## トラブルシューティング

### `ImportError: No module named 'src'`

```bash
pip install -e .
```

を実行してください。

### Playwright ブラウザが見つからない

```bash
playwright install chromium
```

を実行して Chromium をインストールしてください。

### スクレイピングが失敗する

- Google Flights のページ構造が変更された可能性があります
- ネットワーク接続を確認してください
- `--headful` オプションでブラウザを表示して動作を確認できます（開発時のみ）

### 空港コードについて

**エリアコードは自動的に具体的な空港に展開されます:**

- `TYO` → `NRT,HND`（成田、羽田）
- `NYC` → `JFK,LGA,EWR`（ニューヨーク3空港）
- `LON` → `LHR,LGW,STN`（ロンドン3空港）
- `PAR` → `CDG,ORY`（パリ2空港）

**推奨:** より正確な結果を得るには、具体的な空港コード（例: `NRT`, `LAX`）を使用してください。

### テストが失敗する

```bash
pytest tests/ -v --tb=short
```

で詳細を確認してください。

## Claude Code 分析プロンプトについて

`src/prompts.py` には7つの分析プロンプトが定義されています。これらは Claude Code との対話時の参考として利用できます。

自動分析は行わず、ユーザーが必要に応じて Claude Code に質問する形式を採用しています。これにより:

- API コストがかからない
- より柔軟な分析が可能
- ユーザーの状況に合わせた深掘りができる

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まず Issue を開いて変更内容を説明してください。

## サポート

問題が発生した場合は、GitHub Issues でお知らせください。

---

**GitHub:** https://github.com/tndhk/No36_flight_cheap

**最終更新:** 2026-01-14

# Flight Cheap CLI

航空券を安く取得するための AI 分析ツール。Google Flights のデータと Gemini API による 7 つの分析プロンプトで、価格最適化戦略を提案します。

## 機能

**7つの AI 分析プロンプト:**

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

### 4. API キーを設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して、API キーを設定します。

## API キー取得

### SerpAPI (Google Flights)

1. https://serpapi.com/ にアクセス
2. アカウント作成（Google/GitHub でログイン可能）
3. Dashboard から API キーをコピー
4. `.env` の `SERPAPI_KEY` に貼り付け

**無料枠:** 月 100 回の検索

### Gemini API (Google AI)

1. https://ai.google.dev/ にアクセス
2. 「Get API Key」をクリック
3. Google アカウントでサイン イン
4. API キーをコピー
5. `.env` の `GEMINI_API_KEY` に貼り付け

**無料枠:** 15 RPM (1 分間に 15 リクエスト上限)

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

### ヘルプ表示

```bash
flight-cheap search --help
```

## 出力例

```
Flight Cheap Analysis: TYO → LAX (2025-03-01)
============================================================

[Hidden Route Scanner]
----------------------------------------
[7つの分析結果がターミナルに表示されます...]

[Price Manipulation Detector]
----------------------------------------
...

============================================================
SUMMARY
----------------------------------------
Total Analysis Prompts: 7
Execution Time: 12.34s
```

## プロジェクト構成

```
flight_cheap/
├── src/
│   ├── __init__.py
│   ├── prompts.py      # 7つのプロンプト定義
│   ├── fetcher.py      # SerpAPI 連携
│   ├── analyzer.py     # Gemini API 連携 + 非同期処理
│   ├── formatter.py    # 出力整形 (Rich ライブラリ)
│   └── cli.py          # Click CLI メイン
├── tests/
│   ├── test_prompts.py       # 16 テスト
│   ├── test_fetcher.py       # 13 テスト
│   ├── test_analyzer.py      # 11 テスト
│   ├── test_formatter.py     # 9 テスト
│   └── test_cli.py           # 10 テスト
├── .env.example        # API キー テンプレート
├── .gitignore
├── pyproject.toml      # 依存関係 + プロジェクト設定
├── pytest.ini          # pytest 設定
└── README.md           # このファイル
```

## 技術スタック

- **言語:** Python 3.11+
- **Data Fetching:** SerpAPI (Google Flights)
- **LLM:** Google Gemini API
- **CLI:** Click
- **出力整形:** Rich
- **非同期:** asyncio (3並列制限)
- **テスト:** pytest (59 テスト)

## 開発者向け情報

### テスト実行

全テストを実行：

```bash
pytest tests/ -v
```

特定のテストのみ：

```bash
pytest tests/test_prompts.py -v
```

### 開発環境セットアップ

```bash
pip install -e ".[dev]"
```

このコマンドで以下が追加インストールされます：
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

### `API key not found` エラー

`.env` ファイルが存在するか確認：

```bash
cat .env
```

`SERPAPI_KEY` と `GEMINI_API_KEY` が正しく設定されているか確認してください。

### 分析が遅い

- Gemini API の無料枠は **15 RPM** の制限があります
- 7つの分析が並列実行されるため、複数回検索するとレート制限に達することがあります
- 1 分以上待ってから再度実行してください

### テストが失敗する

```bash
pytest tests/ -v --tb=short
```

で詳細を確認してください。

## API 仕様

### SerpAPI (Google Flights)

検索パラメータ：
- `departure_id`: 出発空港コード (例: TYO)
- `arrival_id`: 到着空港コード (例: LAX)
- `outbound_date`: 出発日 (YYYY-MM-DD)
- `return_date`: 帰着日 (YYYY-MM-DD、往復の場合)

### Gemini API

- モデル: `gemini-pro`
- 入力: システムプロンプト + ユーザープロンプト + フライトデータ
- 出力: 分析結果テキスト

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まず Issue を開いて変更内容を説明してください。

## サポート

問題が発生した場合は、GitHub Issues でお知らせください。

---

**GitHub:** https://github.com/tndhk/No36_flight_cheap

**最終更新:** 2025-01-13

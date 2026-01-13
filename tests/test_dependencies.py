def test_pyproject_has_playwright():
    """pyproject.tomlにplaywrightが含まれていることを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "playwright" in content


def test_pyproject_no_serpapi():
    """pyproject.tomlにserpapiが含まれていないことを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "serpapi" not in content


def test_pyproject_no_google_generativeai():
    """pyproject.tomlにgoogle-generativeaiが含まれていないことを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "google-generativeai" not in content


def test_env_example_no_serpapi_key():
    """.env.exampleにSERPAPI_KEYが含まれていないことを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "SERPAPI_KEY" not in content
    assert "serpapi" not in content.lower()


def test_env_example_no_gemini_key():
    """.env.exampleにGEMINI_API_KEYが含まれていないことを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "GEMINI_API_KEY" not in content
    assert "gemini" not in content.lower()


def test_env_example_has_playwright_instructions():
    """.env.exampleにPlaywrightのインストール手順が含まれていることを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "playwright install" in content.lower()


def test_readme_no_serpapi_references():
    """README.mdにSerpAPIの参照が含まれていないことを確認"""
    with open("README.md") as f:
        content = f.read()
    # セクションタイトルや説明からSerpAPIへの言及を削除
    assert "SerpAPI" not in content
    assert "serpapi.com" not in content


def test_readme_no_gemini_references():
    """README.mdにGemini APIの参照が含まれていないことを確認"""
    with open("README.md") as f:
        content = f.read()
    # Gemini API取得方法やai.google.devへの参照を削除
    assert "GEMINI_API_KEY" not in content
    assert "ai.google.dev" not in content
    assert "Google Gemini API" not in content


def test_readme_has_playwright_setup():
    """README.mdにPlaywrightのセットアップ手順が含まれていることを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "playwright install" in content.lower()
    assert "chromium" in content.lower()


def test_readme_has_claude_code_workflow():
    """README.mdにClaude Code対話ワークフローの説明が含まれていることを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "Claude Code" in content
    assert "対話" in content or "interactive" in content.lower()

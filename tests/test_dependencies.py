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

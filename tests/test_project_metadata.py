from pathlib import Path


def test_sales_project_has_docs_and_ignore_rules():
    assert Path('docs').exists()
    assert 'app.db' in Path('.gitignore').read_text(encoding='utf-8')

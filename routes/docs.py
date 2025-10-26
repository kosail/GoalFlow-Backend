from flask import Blueprint, render_template
import markdown2
from pathlib import Path

docs_bp = Blueprint("docs", __name__, url_prefix="/docs")

@docs_bp.route("/")
def show_docs():
    md_file = Path("api.md")
    if not md_file.exists():
        return "<h1>Documentation not found</h1>", 404

    html_content = markdown2.markdown(
        md_file.read_text(),
        extras=["fenced-code-blocks", "tables", "toc"]
    )
    return render_template("docs.html", html_content=html_content)

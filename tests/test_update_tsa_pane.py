import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import update_tsa_pane as u  # noqa: E402

# Minimal slice of the t.me/s/<channel> HTML shape: two messages, latest last.
SAMPLE_HTML = """
<div class="tgme_widget_message_text">OLD signal · ignore me</div>
<div class="tgme_widget_message_text">📈 EUR/USD LONG<br>Entry 1.0850<br>SL 1.0820<br>TP 1.0920</div>
"""

def test_fetch_latest_returns_last_message_as_text():
    msg = u.fetch_latest_message("anychannel", _html=SAMPLE_HTML)
    assert msg.startswith("📈 EUR/USD LONG")
    assert "TP 1.0920" in msg
    assert "OLD signal" not in msg          # must take the LAST block
    assert "\n" in msg                       # <br> became newlines

def test_fetch_latest_returns_none_when_no_messages():
    assert u.fetch_latest_message("anychannel", _html="<div>nothing</div>") is None

def test_truncate_caps_lines_and_appends_notice():
    text = "\n".join(f"line {i}" for i in range(20))
    out = u.truncate(text, max_lines=12)
    assert out.count("\n") == 12            # 12 lines + the notice line
    assert out.endswith("… view full signal on Telegram")
    assert "line 0" in out and "line 11" in out and "line 12" not in out

def test_truncate_leaves_short_text_unchanged():
    assert u.truncate("a\nb\nc", max_lines=12) == "a\nb\nc"

def test_render_pane_escapes_html_and_stamps_time():
    now = datetime(2026, 6, 8, 14, 30, tzinfo=timezone.utc)
    html_out = u.render_pane("<script>x</script>\nsafe", now=now)
    assert "<script>" not in html_out        # escaped
    assert "&lt;script&gt;" in html_out
    assert "<br>" in html_out                # newline became <br>
    assert "2026-06-08 14:30 UTC" in html_out

def test_rewrite_index_replaces_between_markers(tmp_path):
    idx = tmp_path / "index.html"
    idx.write_text("A<!-- TSA:START -->OLD<!-- TSA:END -->B", encoding="utf-8")
    changed = u.rewrite_index("NEW", index_path=idx)
    assert changed is True
    out = idx.read_text(encoding="utf-8")
    assert "OLD" not in out and "NEW" in out
    assert out.startswith("A<!-- TSA:START -->") and out.endswith("<!-- TSA:END -->B")

def test_rewrite_index_noop_when_identical(tmp_path):
    idx = tmp_path / "index.html"
    idx.write_text("A<!-- TSA:START -->\nNEW\n<!-- TSA:END -->B", encoding="utf-8")
    assert u.rewrite_index("NEW", index_path=idx) is False

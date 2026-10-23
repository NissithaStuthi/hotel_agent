"""Console utility with Windows UTF-8 encoding support and styled banners."""
import sys

def configure_utf8_output():
    """Ensures stdout and stderr handle UTF-8 symbols cleanly on Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

configure_utf8_output()

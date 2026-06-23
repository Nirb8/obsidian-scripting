import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Load .env from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

NOTES_DIR = os.getenv("NOTES_DIR")
if not NOTES_DIR:
    raise ValueError("NOTES_DIR not set in .env file")

# ── Date range ────────────────────────────────────────────────────────────────
START_DAY = date.today()  # most recent day, iterate backwards from here
END_DAY   = date(2026, 6, 1)        # stop at today's date (inclusive)
# ─────────────────────────────────────────────────────────────────────────────

NAV_PREFIX_MARKER = "<!-- nav-links -->\n"


def nav_block(prev_date: date | None, next_date: date | None) -> str:
    """Return the two-line nav string to prepend to a note."""
    prev_link = f"[[{prev_date}]]" if prev_date else "*(no previous)*"
    next_link = f"[[{next_date}]]" if next_date else "*(no next)*"
    return f"{NAV_PREFIX_MARKER}{prev_link}     {next_link}\n\n"


def note_path(d: date) -> str:
    return os.path.join(NOTES_DIR, f"{d}.md")


def ensure_file(d: date, prev_date: date | None, next_date: date | None) -> None:
    """Create the file if it doesn't exist, then prepend/replace the nav block."""
    path = note_path(d)
    nav = nav_block(prev_date, next_date)

    if not os.path.exists(path):
        print(f"  [created]  {d}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(nav)
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace existing nav block, or prepend a fresh one
    if content.startswith(NAV_PREFIX_MARKER):
        # Strip old nav block (marker line + nav line + blank line)
        rest = content[len(NAV_PREFIX_MARKER):]
        rest = rest.split("\n", 2)          # [nav_line, "", remainder...]
        content = rest[2] if len(rest) > 2 else ""

    new_content = nav + content
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  [updated]  {d}.md")


def main() -> None:
    os.makedirs(NOTES_DIR, exist_ok=True)

    current = START_DAY
    delta   = timedelta(days=1)

    while current >= END_DAY:
        prev_date = current - delta
        next_date = current + delta

        # Only link to neighbours that exist (or will be created this run)
        # because we iterate backwards, the "next" file was already handled.
        # For "prev", we create it below if missing — so always include it.
        ensure_file(current, prev_date, next_date)
        current -= delta
        # print(f"Processed {current + delta}...")

    print("\nDone.")


if __name__ == "__main__":
    main()
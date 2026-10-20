"""Build a presentation in place, or all presentations in this repository."""
import argparse
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "types"))
from contracts import PresentationError
from sources import discover
from export import build


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="Build repository docs/presentations/*")
    scope.add_argument("--presentation", type=Path, help="A single source presentation folder")
    parser.add_argument("--check", action="store_true", help="Validate sources without writing outputs")
    parser.add_argument("--narration", choices=("intro", "detailed"), default="intro",
                        help="Intro preserves the existing deck; detailed adds ordered explanations")
    args = parser.parse_args()
    try:
        if args.all:
            collection = SKILL.parents[2] / "docs" / "presentations"
            decks = sorted(p for p in collection.iterdir() if p.is_dir())
        else:
            decks = [args.presentation]
        if not decks:
            raise PresentationError("No presentation folders found")
        for deck in decks:
            if args.check:
                slides = discover(deck, args.narration)
                print(f"PASS {deck.name}: {len(slides)} slides; no writes")
            else:
                result = build(deck, args.narration)
                print(f"BUILT {result.pptx} ({result.slide_count} slides)")
                for warning in result.warnings:
                    print(f"WARNING {warning}")
        return 0
    except (PresentationError, OSError, ValueError) as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

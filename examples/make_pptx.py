from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from drawingml_svg.pptx import build_slide_xml, prepare_slide_media, svg_to_pptx, write_pptx

__all__ = ["build_slide_xml", "main", "prepare_slide_media", "write_pptx"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="make_pptx.py")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("svgraph-sample.pptx"))
    args = parser.parse_args(argv)

    try:
        svg_to_pptx(args.input.read_text(encoding="utf-8"), args.output)
    except (ET.ParseError, OSError, ValueError) as exc:
        parser.exit(1, f"{parser.prog}: error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

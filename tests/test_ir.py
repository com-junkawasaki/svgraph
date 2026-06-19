from __future__ import annotations

import json

from drawingml_svg import svg_to_ir, svg_to_pptx_ir
from drawingml_svg.ir import svg_ir_to_json, svg_pptx_ir_to_json


def test_svg_ir_preserves_metadata_data_attributes_and_dependencies() -> None:
    svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <metadata>{"title": "System", "relations": [{"from": "api", "to": "db"}]}</metadata>
  <defs>
    <linearGradient id="g"><stop offset="0" stop-color="red"/></linearGradient>
  </defs>
  <rect id="api" data-kind="service" data-bind="svc.api" fill="url(#g)" stroke="#fef9c3" x="1" y="2" width="3" height="4"/>
  <use id="api-copy" href="#api" x="10"/>
</svg>
"""

    ir = svg_to_ir(svg)

    assert ir.version == "0.1"
    assert ir.metadata["json"] == {"title": "System", "relations": [{"from": "api", "to": "db"}]}
    assert ir.presentation.kind == "pptxsvg"
    assert ir.presentation.slide_size == (100.0, 50.0)
    assert ir.presentation.slides[0].slide_id == "slide-1"
    assert ir.presentation.parts[-1].part_name == "/ppt/slides/slide1.xml"
    rect = ir.root.children[1]
    assert rect.tag == "rect"
    assert rect.data == {"bind": "svc.api", "kind": "service"}
    assert rect.dependencies[0].kind == "paint-server"
    assert rect.dependencies[0].target == "#g"
    assert "#fef9c3" not in [dep.target for dep in ir.dependencies]
    use = ir.root.children[2]
    assert use.dependencies[0].kind == "href"
    assert use.dependencies[0].target == "#api"
    assert [dep.target for dep in ir.dependencies] == ["#g", "#api"]


def test_svg_ir_json_cli_payload_is_serializable() -> None:
    payload = svg_ir_to_json(
        """<svg xmlns="http://www.w3.org/2000/svg"><rect data-kind="table" width="10" height="10"/></svg>"""
    )

    data = json.loads(payload)

    assert data["root"]["children"][0]["data"] == {"kind": "table"}
    assert data["presentation"]["kind"] == "pptxsvg"


def test_svg_pptx_ir_discovers_declared_slides() -> None:
    svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <metadata>{"presentation": {"slideSize": {"width": 1280, "height": 720}}}</metadata>
  <g id="intro" data-kind="slide" data-title="Intro" viewBox="0 0 1280 720">
    <title>Opening</title>
    <rect data-role="title" width="300" height="80"/>
  </g>
  <svg id="detail" data-role="slide" viewBox="0 0 960 540">
    <metadata>{"title": "Detail"}</metadata>
    <rect data-kind="table" width="600" height="300"/>
  </svg>
</svg>
"""

    presentation = svg_to_pptx_ir(svg)

    assert presentation.kind == "pptxsvg"
    assert presentation.slide_size == (1280.0, 720.0)
    assert [slide.slide_id for slide in presentation.slides] == ["intro", "detail"]
    assert [slide.title for slide in presentation.slides] == ["Intro", "Detail"]
    assert presentation.slides[1].view_box == (0.0, 0.0, 960.0, 540.0)
    assert [part.part_name for part in presentation.parts[-2:]] == ["/ppt/slides/slide1.xml", "/ppt/slides/slide2.xml"]
    assert [part.source_node_id for part in presentation.parts[-2:]] == ["n0.0", "n0.1"]


def test_svg_pptx_ir_json_cli_payload_is_serializable() -> None:
    payload = svg_pptx_ir_to_json(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"><g data-slide="1"/></svg>"""
    )

    data = json.loads(payload)

    assert data["kind"] == "pptxsvg"
    assert data["slide_size"] == [16.0, 9.0]
    assert data["slides"][0]["slide_id"] == "1"
    assert data["parts"][-1]["kind"] == "slide"

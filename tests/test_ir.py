from __future__ import annotations

import json

from drawingml_svg import svg_to_ir
from drawingml_svg.ir import svg_ir_to_json


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

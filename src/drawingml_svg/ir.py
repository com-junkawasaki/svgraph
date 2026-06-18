from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from xml.etree import ElementTree as ET

from .converter import _href, _local_name


IRI_RE = re.compile(r"url\(\s*['\"]?(#[^)'\"]+)['\"]?\s*\)")
HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


@dataclass(frozen=True)
class SvgIRDocument:
    version: str
    root: "SvgIRNode"
    metadata: dict[str, object]
    dependencies: tuple["SvgIRDependency", ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SvgIRNode:
    node_id: str
    tag: str
    attributes: dict[str, str]
    data: dict[str, str]
    metadata: dict[str, object]
    dependencies: tuple["SvgIRDependency", ...]
    children: tuple["SvgIRNode", ...]
    text: str | None = None


@dataclass(frozen=True)
class SvgIRDependency:
    kind: str
    source: str
    target: str
    attribute: str | None = None


def svg_to_ir(svg_text: str) -> SvgIRDocument:
    """Parse SVG into a metadata-preserving IR for downstream emitters."""

    root = ET.fromstring(svg_text)
    root_node = _node_to_ir(root, "n0")
    return SvgIRDocument(
        version="0.1",
        root=root_node,
        metadata=root_node.metadata,
        dependencies=_collect_node_dependencies(root_node),
    )


def svg_ir_to_json(svg_text: str) -> str:
    return json.dumps(svg_to_ir(svg_text).to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _node_to_ir(element: ET.Element, node_id: str) -> SvgIRNode:
    tag = _local_name(element.tag)
    attributes = _attributes(element)
    data = _data_attributes(attributes)
    metadata = _metadata(element)
    dependencies = _dependencies(element, attributes)
    children = tuple(
        _node_to_ir(child, f"{node_id}.{index}")
        for index, child in enumerate(list(element))
        if _local_name(child.tag) != "metadata"
    )
    text = element.text.strip() if element.text and element.text.strip() else None
    return SvgIRNode(
        node_id=node_id,
        tag=tag,
        attributes=attributes,
        data=data,
        metadata=metadata,
        dependencies=dependencies,
        children=children,
        text=text,
    )


def _attributes(element: ET.Element) -> dict[str, str]:
    return {str(_local_name(name)): value for name, value in sorted(element.attrib.items())}


def _data_attributes(attributes: dict[str, str]) -> dict[str, str]:
    return {name[5:]: value for name, value in attributes.items() if name.startswith("data-")}


def _metadata(element: ET.Element) -> dict[str, object]:
    result: dict[str, object] = {}
    for child in list(element):
        if _local_name(child.tag) != "metadata":
            continue
        text = "".join(child.itertext()).strip()
        if text:
            result["text"] = text
            parsed = _json_metadata(text)
            if parsed is not None:
                result["json"] = parsed
        xml_children = [grandchild for grandchild in list(child)]
        if xml_children:
            result["xml"] = "".join(ET.tostring(grandchild, encoding="unicode") for grandchild in xml_children)
    return result


def _json_metadata(text: str) -> object | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _dependencies(element: ET.Element, attributes: dict[str, str]) -> tuple[SvgIRDependency, ...]:
    tag = _local_name(element.tag)
    source = attributes.get("id", tag)
    deps: list[SvgIRDependency] = []
    href = _href(element)
    if href:
        deps.append(SvgIRDependency("href", source, href, "href"))
    for name, value in attributes.items():
        if name == "href":
            continue
        if value.startswith("#") and not HEX_COLOR_RE.match(value):
            deps.append(SvgIRDependency("reference", source, value, name))
        for match in IRI_RE.finditer(value):
            deps.append(SvgIRDependency("paint-server", source, match.group(1), name))
    return tuple(deps)


def _collect_node_dependencies(node: SvgIRNode) -> tuple[SvgIRDependency, ...]:
    deps = list(node.dependencies)
    for child in node.children:
        deps.extend(_collect_node_dependencies(child))
    return tuple(deps)

"""Legacy import path and pre-SVGraph aliases."""

import warnings

from .svgraph import (
    SVGraphDependency as _SVGraphDependency,
    SVGraphDocument as _SVGraphDocument,
    SVGraphGuide as _SVGraphGuide,
    SVGraphNode as _SVGraphNode,
    SVGraphPackagePart as _SVGraphPackagePart,
    SVGraphPresentation as _SVGraphPresentation,
    SVGraphRuler as _SVGraphRuler,
    SVGraphSlide as _SVGraphSlide,
    SVGraphTemplate as _SVGraphTemplate,
    SVGraphTextStyle as _SVGraphTextStyle,
    svg_svgraph_presentation_to_json as _svg_svgraph_presentation_to_json,
    svg_svgraph_to_json as _svg_svgraph_to_json,
    svg_to_svgraph as _svg_to_svgraph,
    svg_to_svgraph_presentation as _svg_to_svgraph_presentation,
)

SvgIRDocument = _SVGraphDocument
SvgIRNode = _SVGraphNode
SvgIRDependency = _SVGraphDependency
SvgIRPresentation = _SVGraphPresentation
SvgIRSlide = _SVGraphSlide
SvgIRPackagePart = _SVGraphPackagePart
SvgIRTemplate = _SVGraphTemplate
SvgIRGuide = _SVGraphGuide
SvgIRRuler = _SVGraphRuler
SvgIRTextStyle = _SVGraphTextStyle


def svg_to_ir(svg_text: str) -> _SVGraphDocument:
    """Legacy alias for :func:`drawingml_svg.svgraph.svg_to_svgraph`."""

    _warn_legacy("svg_to_ir()", "drawingml_svg.svgraph.svg_to_svgraph()")
    return _svg_to_svgraph(svg_text)


def svg_to_pptx_ir(svg_text: str) -> _SVGraphPresentation:
    """Legacy alias for :func:`drawingml_svg.svgraph.svg_to_svgraph_presentation`."""

    _warn_legacy("svg_to_pptx_ir()", "drawingml_svg.svgraph.svg_to_svgraph_presentation()")
    return _svg_to_svgraph_presentation(svg_text)


def svg_ir_to_json(svg_text: str) -> str:
    _warn_legacy("svg_ir_to_json()", "drawingml_svg.svgraph.svg_svgraph_to_json()")
    return _svg_svgraph_to_json(svg_text)


def svg_pptx_ir_to_json(svg_text: str) -> str:
    _warn_legacy("svg_pptx_ir_to_json()", "drawingml_svg.svgraph.svg_svgraph_presentation_to_json()")
    return _svg_svgraph_presentation_to_json(svg_text)


def _warn_legacy(name: str, replacement: str) -> None:
    warnings.warn(
        f"{name} is deprecated; use {replacement}.",
        DeprecationWarning,
        stacklevel=2,
    )


__all__ = [
    "SvgIRDependency",
    "SvgIRDocument",
    "SvgIRGuide",
    "SvgIRNode",
    "SvgIRPackagePart",
    "SvgIRPresentation",
    "SvgIRRuler",
    "SvgIRSlide",
    "SvgIRTemplate",
    "SvgIRTextStyle",
    "svg_ir_to_json",
    "svg_pptx_ir_to_json",
    "svg_to_ir",
    "svg_to_pptx_ir",
]

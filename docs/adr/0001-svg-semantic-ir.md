# ADR 0001: SVG Semantic IR

## Status

Accepted

## Context

SVG can carry visual geometry, document metadata, and application-specific data in one file. The current converter focuses on editable DrawingML fragments, but an application-level pipeline also needs to preserve structure, inferred meaning, and dependencies so the same SVG source can later emit Android VectorDrawable, DrawingML, PresentationML, or other targets.

## Decision

Introduce an SVG-based intermediate representation, exposed as `svg_to_ir()`, that preserves:

- element tree structure with stable node ids
- normal SVG attributes
- `data-*` attributes as application data
- local `<metadata>` text, XML, and JSON payloads
- dependencies such as `href`, `xlink:href`, `url(#id)` paint servers, markers, clipping, masks, symbols, and other local references
- a presentation/package view named `pptxsvg`

The IR is intentionally independent of a specific output format. Target emitters consume the IR and decide whether a node maps to a native object, a grouped shape, a raster fallback, or an application sidecar.

## IR Shape

```json
{
  "version": "0.1",
  "metadata": {},
  "dependencies": [],
  "presentation": {
    "kind": "pptxsvg",
    "slide_size": [1280, 720],
    "slides": [],
    "parts": []
  },
  "root": {
    "node_id": "n0",
    "tag": "svg",
    "attributes": {},
    "data": {},
    "metadata": {},
    "dependencies": [],
    "children": []
  }
}
```

Nodes keep visual SVG data and semantic data together. This makes the SVG itself the source of truth while giving non-SVG targets a normalized read model.

## Metadata Convention

Application data should prefer either JSON in `<metadata>` or small scalar `data-*` attributes:

```xml
<svg viewBox="0 0 400 240">
  <metadata>
    {
      "title": "Architecture",
      "entities": [{"id": "api", "type": "service"}],
      "relations": [{"from": "api", "to": "db", "type": "depends-on"}]
    }
  </metadata>
  <rect id="api" data-kind="service" data-layer="backend" x="20" y="20" width="120" height="60"/>
  <rect id="db" data-kind="database" x="220" y="20" width="120" height="60"/>
</svg>
```

Recommended fields:

- `data-kind`: semantic object type, such as `service`, `database`, `table`, `cell`, `actor`, `flow`, or `annotation`
- `data-role`: presentation role, such as `title`, `label`, `caption`, `node`, `edge`, or `container`
- `data-bind`: external application id or model path
- `data-group`: logical group independent from SVG `<g>`
- `data-order`: application reading or animation order

## PPTXSVG Presentation View

`pptxsvg` is the SVG IR projection for creating a full `.pptx` package rather than a single DrawingML shape fragment. It is not a new rendering format; it is a package intent over the same SVG source.

Slide boundaries are discovered in this order:

- any element with `data-kind="slide"`
- any element with `data-role="slide"`
- any element with `data-slide="..."`
- otherwise, the root `<svg>` is treated as one slide

Slide size is discovered in this order:

- root metadata: `{"presentation": {"slideSize": {"width": 1280, "height": 720}}}`
- root `viewBox`
- first slide `viewBox`

Example:

```xml
<svg viewBox="0 0 1280 720">
  <metadata>{"presentation": {"slideSize": {"width": 1280, "height": 720}}}</metadata>
  <g id="cover" data-kind="slide" data-title="Cover">
    <text data-role="title">Quarterly Review</text>
  </g>
  <g id="system" data-kind="slide" data-title="System">
    <rect id="api" data-kind="service"/>
    <rect id="db" data-kind="database"/>
  </g>
</svg>
```

The package emitter can then map:

- each slide node to `ppt/slides/slideN.xml`
- the `parts` list to the required package blueprint, including presentation, slide master, slide layout, theme, and slide parts
- root presentation metadata to `ppt/presentation.xml`, theme, layout, notes, tags, or custom XML
- semantic `data-kind="table"` / `data-kind="cell"` nodes to native PresentationML tables where possible
- semantic relations to connectors when they have visual counterparts
- unresolved semantics to a package sidecar or custom XML part

## Target Mapping

### Android VectorDrawable / DrawableXML

VectorDrawable is a visual vector format. It has no native table, rich metadata, dependency graph, or presentation object model. Emitters should:

- map supported geometry and paint to native vector paths/groups
- flatten unsupported semantics into visual groups
- preserve IR metadata outside the drawable as a sidecar JSON when semantic round-trip is required

### DrawingML

DrawingML can represent editable shapes, text, tables, and some semantic grouping. Emitters should:

- use native DrawingML tables only when the IR identifies table semantics or the geometry is clearly table-like
- keep per-node provenance in non-visual properties where package context allows it
- preserve unsupported semantics in a sidecar when fragment-only output has no safe storage location

### PresentationML

PresentationML can add slide-level structure beyond DrawingML fragments. Emitters should:

- map IR groups to slide shape trees
- map relationships to connectors when they are visually represented
- map `data-order` and metadata to animation, reading order, notes, custom XML, or tags when the package writer supports it
- use `pptxsvg` as the package-level contract instead of treating `svg_to_drawingml()` output as a whole deck

## Consequences

The converter remains conservative and deterministic. The IR gives the app a richer layer for inference and multi-target expansion without forcing every semantic concept into DrawingML or DrawableXML, where many of those concepts do not exist natively.

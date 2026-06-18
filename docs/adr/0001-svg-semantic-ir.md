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

The IR is intentionally independent of a specific output format. Target emitters consume the IR and decide whether a node maps to a native object, a grouped shape, a raster fallback, or an application sidecar.

## IR Shape

```json
{
  "version": "0.1",
  "metadata": {},
  "dependencies": [],
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

## Consequences

The converter remains conservative and deterministic. The IR gives the app a richer layer for inference and multi-target expansion without forcing every semantic concept into DrawingML or DrawableXML, where many of those concepts do not exist natively.

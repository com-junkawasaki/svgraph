# Migrating to SVGraph

SVGraph is the canonical project name for the repository, Python distribution, import package, CLI, browser editor, schema, generated artifacts, and presentation metadata.

Legacy names remain only as compatibility surfaces. New code should use the SVGraph names below.

## Name Mapping

| Legacy surface | Canonical SVGraph surface |
| --- | --- |
| `com-junkawasaki/drawingml-svg` | `com-junkawasaki/svgraph` |
| `drawingml-svg` Python distribution | `svgraph` Python distribution |
| `drawingml_svg` import package | `svgraph` import package |
| `drawingml_svg.converter` | `svgraph.converter` |
| `drawingml_svg.coverage` | `svgraph.coverage` |
| `drawingml_svg.pptx` | `svgraph.pptx` |
| `drawingml_svg.svgraph` | `svgraph.model` |
| `drawingml_svg.ir.svg_to_ir()` | `svgraph.model.svg_to_svgraph()` |
| `drawingml_svg.ir.svg_to_pptx_ir()` | `svgraph.model.svg_to_svgraph_presentation()` |
| `ir` CLI command | `svgraph` CLI command |
| `pptxsvg` CLI command | `svgraph-presentation` CLI command |
| `drawingml-svg` executable | `svgraph` executable |

## Python Imports

Use the canonical package for new code:

```python
from svgraph import analyze_svg, svg_to_drawingml, svg_to_pptx, svg_to_svgraph
from svgraph.model import svg_to_svgraph_presentation
```

The `drawingml_svg` package remains installable for existing callers, but its main modules are compatibility wrappers over `svgraph`. Deprecated pre-SVGraph IR APIs continue to emit `DeprecationWarning` and point callers to `svgraph.model`.

## CLI

Use `svgraph` as the executable and command namespace:

```bash
svgraph svg2dml input.svg -o shape.xml
svgraph svg2pptx deck.svg -o deck.pptx
svgraph analyze input.svg
svgraph input.svg
svgraph svgraph-presentation input.svg
python -m svgraph --version
```

Legacy executable and command aliases are retained for compatibility smoke tests and existing automation, not as documentation targets for new integrations.

## Generated Artifacts

Generated files should use `svgraph` naming:

```bash
PYTHONPATH=src python examples/make_pptx.py examples/sample.svg -o tmp/svgraph-sample.pptx
svgraph examples/svgraph.svg > tmp/release-svgraph.json
svgraph svgraph-presentation examples/svgraph.svg > tmp/release-svgraph-presentation.json
```

The browser editor is published at:

```text
https://com-junkawasaki.github.io/svgraph/
```

## Verification

Run the migration guard tests before publishing:

```bash
ruff check .
PYTHONPATH=src pytest -q tests/test_migration.py tests/test_svgraph.py
npm run build:web
```

The full test suite also validates that public links, package metadata, wheel and sdist artifact names, CLI smoke checks, and packaged documentation stay on SVGraph naming.

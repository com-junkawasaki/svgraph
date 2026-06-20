# Security Policy

## Supported versions

Security fixes are handled on the default branch until the project publishes stable release branches.

## Reporting a vulnerability

Please do not open a public issue for a suspected security vulnerability.

Report vulnerabilities through GitHub's private vulnerability reporting for this repository:

<https://github.com/com-junkawasaki/svgraph/security/advisories/new>

If that is not available, contact the maintainer listed in `pyproject.toml`.

Include:

- A description of the issue and its impact.
- A minimal SVG, DrawingML fragment, or command that reproduces the problem.
- Any relevant environment details, such as Python version and operating system.

The project treats untrusted SVG, XML, and OOXML-derived input as potentially hostile. Reports involving parser denial of service, unsafe file access, unexpected network access, or generated package contents are in scope.

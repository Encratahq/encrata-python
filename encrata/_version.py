"""Single source of truth for the package version.

This is the ONE place the version string lives. Hatchling reads it at build
time (see ``[tool.hatch.version]`` in ``pyproject.toml``) and the runtime code
imports it from here, so the value can never drift between the package metadata
and what the SDK reports in its ``User-Agent``.
"""

__version__ = "0.5.0"

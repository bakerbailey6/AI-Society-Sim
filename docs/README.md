# Documentation

This directory contains the Sphinx documentation for the Emergent AI Society Simulator.

## Building the Documentation

### Windows
```bash
sphinx-build -M html . _build
```

### Linux/Mac
```bash
make html
```

## Viewing the Documentation

After building, open `_build/html/index.html` in your web browser.

## Documentation Structure

- `index.rst` - Main documentation entry point
- `overview.rst` - Project overview and goals
- `architecture.rst` - System architecture and module structure
- `design_patterns.rst` - Design patterns used in the project
- `api/modules.rst` - Auto-generated API documentation
- `conf.py` - Sphinx configuration
- `Makefile` - Build commands for Unix systems
- `make.bat` - Build commands for Windows

## Updating the Documentation

1. Edit the relevant `.rst` files
2. Rebuild the documentation using the commands above
3. Review changes in your browser
4. Commit the updated `.rst` files (not the `_build` directory)

## ReadTheDocs Integration

This project is configured for ReadTheDocs hosting. The configuration file `.readthedocs.yaml` in the project root controls the ReadTheDocs build.

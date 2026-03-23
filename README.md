# mkdocs-auto-tags

MkDocs plugin that automatically tags pages based on their position in the navigation hierarchy.

Works with any MkDocs project — single repo, multirepo, or manual nav configuration.

## Installation

```bash
pip install mkdocs-auto-tags
```

## Usage

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - tags
  - auto-tags
```

> **Note:** The `tags` plugin must be listed before `auto-tags`.

Every page will be automatically tagged with its parent navigation section name. For example, a page under `API > Authentication` gets tagged with `Authentication`.

## Configuration

```yaml
plugins:
  - auto-tags:
      enabled: true        # Enable/disable the plugin (default: true)
      all_ancestors: false  # Tag with all ancestor sections, not just the immediate parent (default: false)
```

### `all_ancestors`

When `false` (default), a page under `Development > API > Authentication` gets a single tag: `Authentication`.

When `true`, the same page gets three tags: `Development`, `API`, `Authentication`.

## Example

Given this navigation structure:

```
Development/
  API/
    Authentication/
      README.md      → tagged: Authentication
      deployment.md  → tagged: Authentication
    Deployment/
      README.md      → tagged: Deployment
  Infrastructure/
    README.md        → tagged: Infrastructure
```

Pages that already have tags in their front matter will keep them — the plugin appends without duplicating.

## Compatibility

- MkDocs >= 1.4
- Python >= 3.9
- Works with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme
- Works with [mkdocs-multirepo-plugin](https://github.com/jdoiro3/mkdocs-multirepo-plugin)

## License

MIT

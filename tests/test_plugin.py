"""Tests for mkdocs-auto-tags plugin."""

from unittest.mock import MagicMock

from mkdocs_auto_tags.plugin import AutoTagsPlugin


def make_page(parents=None, existing_tags=None):
    """Create a mock MkDocs page with a parent chain."""
    page = MagicMock()
    page.meta = {}
    if existing_tags:
        page.meta["tags"] = existing_tags

    if parents:
        prev = None
        for title in parents:
            section = MagicMock()
            section.title = title
            section.parent = prev
            prev = section
        page.parent = prev
    else:
        page.parent = None

    return page


def make_plugin(enabled=True, paths=None, all_ancestors=False):
    plugin = AutoTagsPlugin()
    plugin.config = MagicMock()
    plugin.config.enabled = enabled
    plugin.config.paths = paths or []
    plugin.config.all_ancestors = all_ancestors
    plugin._prefixes = sorted(
        [p.strip("/").split("/") for p in plugin.config.paths],
        key=len,
        reverse=True,
    )
    return plugin


class TestDefaultMode:
    def test_immediate_parent(self):
        plugin = make_plugin()
        page = make_page(parents=["Development", "API", "Authentication"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_all_ancestors(self):
        plugin = make_plugin(all_ancestors=True)
        page = make_page(parents=["Development", "API", "Authentication"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Development", "API", "Authentication"]

    def test_no_parent(self):
        plugin = make_plugin()
        page = make_page()

        result = plugin.on_page_markdown("# Hello", page, {}, [])

        assert result == "# Hello"
        assert page.meta.get("tags") is None

    def test_preserves_existing_tags(self):
        plugin = make_plugin()
        page = make_page(parents=["API", "Authentication"], existing_tags=["custom"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["custom", "Authentication"]

    def test_no_duplicate_tags(self):
        plugin = make_plugin()
        page = make_page(
            parents=["API", "Authentication"], existing_tags=["Authentication"]
        )

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_single_parent(self):
        plugin = make_plugin()
        page = make_page(parents=["Parent"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Parent"]


class TestPrefixMode:
    def test_basic_prefix(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(parents=["Development", "API", "Authentication"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_multiple_prefixes(self):
        plugin = make_plugin(paths=["Development/API", "Projects"])
        page = make_page(parents=["Projects", "P1", "modules", "test"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["P1"]

    def test_longest_prefix_wins(self):
        plugin = make_plugin(paths=["Development", "Development/API"])
        page = make_page(parents=["Development", "API", "Authentication"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_shorter_prefix_fallback(self):
        plugin = make_plugin(paths=["Development", "Development/API"])
        page = make_page(parents=["Development", "Infrastructure", "docs"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Infrastructure"]

    def test_no_matching_prefix(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(parents=["Projects", "P1"])

        result = plugin.on_page_markdown("# Hello", page, {}, [])

        assert result == "# Hello"
        assert page.meta.get("tags") is None

    def test_prefix_is_exact_ancestors(self):
        """Prefix matches all ancestors exactly — no section left to tag."""
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(parents=["Development", "API"])

        result = plugin.on_page_markdown("# Hello", page, {}, [])

        assert result == "# Hello"
        assert page.meta.get("tags") is None

    def test_preserves_existing_tags(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(
            parents=["Development", "API", "Authentication"],
            existing_tags=["custom"],
        )

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["custom", "Authentication"]

    def test_no_duplicate_tags(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(
            parents=["Development", "API", "Authentication"],
            existing_tags=["Authentication"],
        )

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_deeply_nested_page(self):
        """Only the first section after prefix becomes a tag."""
        plugin = make_plugin(paths=["Projects"])
        page = make_page(parents=["Projects", "P1", "modules", "test"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["P1"]

    def test_trailing_slash_in_prefix(self):
        plugin = make_plugin(paths=["Development/API/"])
        page = make_page(parents=["Development", "API", "Authentication"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Authentication"]

    def test_no_ancestors(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page()

        result = plugin.on_page_markdown("# Hello", page, {}, [])

        assert result == "# Hello"
        assert page.meta.get("tags") is None


class TestCombined:
    def test_paths_with_all_ancestors(self):
        """All sections after prefix are tagged."""
        plugin = make_plugin(paths=["Projects"], all_ancestors=True)
        page = make_page(parents=["Projects", "P1", "modules", "test"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["Projects", "P1"]

    def test_paths_without_all_ancestors(self):
        """Only first section after prefix is tagged."""
        plugin = make_plugin(paths=["Projects"], all_ancestors=False)
        page = make_page(parents=["Projects", "P1", "modules", "test"])

        plugin.on_page_markdown("# Hello", page, {}, [])

        assert page.meta["tags"] == ["P1"]


class TestDisabled:
    def test_disabled(self):
        plugin = make_plugin(enabled=False, paths=["Development/API"])
        page = make_page(parents=["Development", "API", "Authentication"])

        result = plugin.on_page_markdown("# Hello", page, {}, [])

        assert result == "# Hello"
        assert "tags" not in page.meta

    def test_returns_markdown_unchanged(self):
        plugin = make_plugin(paths=["Development/API"])
        page = make_page(parents=["Development", "API", "Authentication"])
        md = "# Title\n\nSome content"

        result = plugin.on_page_markdown(md, page, {}, [])

        assert result == md

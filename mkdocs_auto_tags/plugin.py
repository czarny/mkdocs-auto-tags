"""Auto-tags plugin for MkDocs.

Automatically tags pages based on their navigation hierarchy.
Works with any MkDocs project — single repo, multirepo, or manual nav.
"""

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin, event_priority


class AutoTagsConfig(Config):
    enabled = config_options.Type(bool, default=True)
    # List of nav path prefixes. Pages under a prefix get tagged with the
    # next nav section after it (or all sections after it when all_ancestors
    # is true). Prefixes are matched longest-first.
    # When not set, tags with immediate parent (or all ancestors if enabled).
    paths = config_options.Type(list, default=[])
    # Include the prefix sections in the tags (or all ancestors when paths
    # is not set) instead of just the first section after the prefix.
    all_ancestors = config_options.Type(bool, default=False)


class AutoTagsPlugin(BasePlugin[AutoTagsConfig]):
    """Tags pages with their navigation section names."""

    def on_config(self, config):
        # Parse and sort prefixes longest-first for greedy matching
        self._prefixes = sorted(
            [p.strip("/").split("/") for p in self.config.paths],
            key=len,
            reverse=True,
        )
        return config

    @event_priority(0)
    def on_page_markdown(self, markdown, page, config, files):
        if not self.config.enabled:
            return markdown

        ancestors = self._get_ancestors(page)
        if not ancestors:
            return markdown

        all_ancestors = self.config.all_ancestors

        if self._prefixes:
            tags_to_add = self._tags_from_prefix(ancestors, all_ancestors)
        elif all_ancestors:
            tags_to_add = ancestors
        else:
            tags_to_add = [ancestors[-1]]

        if not tags_to_add:
            return markdown

        existing_tags = page.meta.get("tags", [])
        if not isinstance(existing_tags, list):
            existing_tags = []

        for tag in tags_to_add:
            if tag not in existing_tags:
                existing_tags.append(tag)

        page.meta["tags"] = existing_tags
        return markdown

    def _get_ancestors(self, page):
        """Walk page.parent chain and return list of ancestor titles."""
        parts = []
        parent = page.parent
        while parent:
            if parent.title:
                parts.insert(0, parent.title)
            parent = parent.parent
        return parts

    def _tags_from_prefix(self, ancestors, all_ancestors):
        """Return sections after the matching prefix.

        When all_ancestors is False, returns only the first section after
        the prefix. When True, returns all sections after the prefix.
        """
        for prefix in self._prefixes:
            plen = len(prefix)
            if (
                len(ancestors) > plen
                and ancestors[:plen] == prefix
            ):
                if all_ancestors:
                    return list(prefix) + [ancestors[plen]]
                return [ancestors[plen]]
        return []

"""
Generic Tag Extraction and Restoration

Supports multiple markup formats:
- HTML: <tag attr="value">...</tag>
- Markdown: **bold**, *italic*, [link](url), `code`
- Custom braces: {variable}, {{placeholder}}
- Custom brackets: [variable]

Auto-detects format from content and preserves tags during translation
using proportional positioning algorithm.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional


class TagFormat(Enum):
    """Supported tag/markup formats"""
    HTML = "html"
    MARKDOWN = "markdown"
    CUSTOM_BRACES = "custom_braces"  # {var}, {{placeholder}}
    CUSTOM_BRACKETS = "custom_brackets"  # [var]
    AUTO = "auto"  # Auto-detect from content


@dataclass
class Tag:
    """Represents a tag/markup element"""
    pos: int  # Character position in text
    content: str  # The tag content (e.g., "<b>", "**", "{name}")
    tag_type: str  # Type identifier (html, markdown, variable, etc.)


class GenericTagExtractor:
    """Extract and restore tags from text in multiple formats"""

    # HTML tags: <tag>, </tag>, <tag attr="value">
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')

    # Markdown patterns
    MD_BOLD_PATTERN = re.compile(r'\*\*[^*]+\*\*')  # **bold**
    MD_ITALIC_PATTERN = re.compile(r'\*[^*]+\*')  # *italic*
    MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')  # [text](url)
    MD_CODE_PATTERN = re.compile(r'`[^`]+`')  # `code`

    # Custom braces: {var}, {{placeholder}}
    BRACE_DOUBLE_PATTERN = re.compile(r'\{\{[^}]+\}\}')  # {{var}}
    BRACE_SINGLE_PATTERN = re.compile(r'\{[^}]+\}')  # {var}

    # Custom brackets: [var]
    BRACKET_PATTERN = re.compile(r'\[[^\]]+\]')  # [var]

    @classmethod
    def detect_format(cls, text: str) -> TagFormat:
        """
        Auto-detect the markup format from text content

        Args:
            text: Text to analyze

        Returns:
            Detected TagFormat
        """
        # Check for HTML tags
        if cls.HTML_TAG_PATTERN.search(text):
            return TagFormat.HTML

        # Check for Markdown (bold, italic, links, code)
        if (cls.MD_BOLD_PATTERN.search(text) or
            cls.MD_ITALIC_PATTERN.search(text) or
            cls.MD_LINK_PATTERN.search(text) or
            cls.MD_CODE_PATTERN.search(text)):
            return TagFormat.MARKDOWN

        # Check for double braces first (more specific)
        if cls.BRACE_DOUBLE_PATTERN.search(text):
            return TagFormat.CUSTOM_BRACES

        # Check for single braces
        if cls.BRACE_SINGLE_PATTERN.search(text):
            return TagFormat.CUSTOM_BRACES

        # Check for brackets
        if cls.BRACKET_PATTERN.search(text):
            return TagFormat.CUSTOM_BRACKETS

        # Default to HTML if no format detected
        return TagFormat.HTML

    @classmethod
    def extract_tags(cls, text: str, format: TagFormat = TagFormat.AUTO) -> Tuple[str, List[Tag]]:
        """
        Extract tags from text, return clean text and tag list

        Args:
            text: Text containing tags
            format: Tag format to use (AUTO for auto-detection)

        Returns:
            Tuple of (clean_text, tags_list)
        """
        if format == TagFormat.AUTO:
            format = cls.detect_format(text)

        tags = []
        clean_text = text

        # Collect all tag matches based on format
        all_matches = []

        if format == TagFormat.HTML:
            for match in cls.HTML_TAG_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'html'))

        elif format == TagFormat.MARKDOWN:
            # Order matters: check longer patterns first
            for match in cls.MD_BOLD_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'md_bold'))
            for match in cls.MD_LINK_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'md_link'))
            for match in cls.MD_CODE_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'md_code'))
            # Italic last to avoid matching bold markers
            for match in cls.MD_ITALIC_PATTERN.finditer(text):
                # Skip if this is part of a bold pattern
                if not any(m[0] <= match.start() < m[0] + len(m[1])
                          for m in all_matches if m[2] == 'md_bold'):
                    all_matches.append((match.start(), match.group(), 'md_italic'))

        elif format == TagFormat.CUSTOM_BRACES:
            # Check double braces first (more specific)
            for match in cls.BRACE_DOUBLE_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'brace_double'))
            for match in cls.BRACE_SINGLE_PATTERN.finditer(text):
                # Skip if this is part of a double brace
                if not any(m[0] <= match.start() < m[0] + len(m[1])
                          for m in all_matches if m[2] == 'brace_double'):
                    all_matches.append((match.start(), match.group(), 'brace_single'))

        elif format == TagFormat.CUSTOM_BRACKETS:
            for match in cls.BRACKET_PATTERN.finditer(text):
                all_matches.append((match.start(), match.group(), 'bracket'))

        # Sort by position (reverse order for removal)
        all_matches.sort(key=lambda x: x[0], reverse=True)

        # Remove overlapping matches (keep the first one encountered)
        filtered_matches = []
        for match in all_matches:
            pos, content, tag_type = match
            # Check if this match overlaps with any already added
            overlaps = any(
                fm[0] <= pos < fm[0] + len(fm[1]) or
                pos <= fm[0] < pos + len(content)
                for fm in filtered_matches
            )
            if not overlaps:
                filtered_matches.append(match)

        # Remove tags from text and store positions
        for pos, content, tag_type in filtered_matches:
            # Calculate position in clean text (before this tag)
            before_tag = text[:pos]
            tags.insert(0, Tag(pos=len(before_tag), content=content, tag_type=tag_type))
            clean_text = clean_text[:pos] + clean_text[pos + len(content):]

        # Clean up extra spaces left after tag removal
        clean_text = re.sub(r' +', ' ', clean_text)  # Multiple spaces
        clean_text = re.sub(r' +([.,!?;:])', r'\1', clean_text)  # Spaces before punctuation

        return clean_text.strip(), tags

    @classmethod
    def restore_tags(cls, translated_text: str, tags: List[Tag], original_text: str) -> str:
        """
        Restore tags into translated text based on proportional positions

        Strategy:
        - Use proportional positioning based on text length
        - Place tags at safe positions (not inside other tags)
        - Preserve original tag order

        Args:
            translated_text: Translated text without tags
            tags: List of tags to restore
            original_text: Original text with tags (for position calculation)

        Returns:
            Translated text with restored tags
        """
        if not tags:
            return translated_text

        result = translated_text
        original_len = len(original_text)
        translated_len = len(translated_text)

        # Sort tags by position for insertion (reverse order)
        sorted_tags = sorted(tags, key=lambda x: x.pos, reverse=True)

        for tag in sorted_tags:
            # Calculate proportional position
            if original_len > 0:
                ratio = tag.pos / original_len
                new_pos = int(ratio * translated_len)
            else:
                new_pos = 0

            # Clamp position to text bounds
            new_pos = max(0, min(new_pos, len(result)))

            # Find safe insertion point (not inside existing tags)
            safe_pos = cls._find_safe_insertion_point(result, new_pos, tag.tag_type)

            # Insert tag
            result = result[:safe_pos] + tag.content + result[safe_pos:]

        return result

    @staticmethod
    def _find_safe_insertion_point(text: str, target_pos: int, tag_type: str) -> int:
        """
        Find a safe position to insert a tag, ensuring we don't break existing tags

        Args:
            text: The text to insert into
            target_pos: The desired insertion position
            tag_type: Type of tag being inserted

        Returns:
            A safe position that won't break existing tags
        """
        # Clamp to text bounds
        target_pos = max(0, min(target_pos, len(text)))

        # Check if we're inside a tag at target_pos
        before_text = text[:target_pos]

        # Check for HTML tags: count < and >
        if '<' in text:
            open_tags = before_text.count('<')
            close_tags = before_text.count('>')
            if open_tags > close_tags:
                # We're inside <>, find the next >
                next_close = text.find('>', target_pos)
                if next_close != -1:
                    return next_close + 1

        # Check for braces: { and }
        if '{' in text:
            open_braces = before_text.count('{')
            close_braces = before_text.count('}')
            if open_braces > close_braces:
                # We're inside {}, find the next }
                next_close = text.find('}', target_pos)
                if next_close != -1:
                    return next_close + 1

        # Check for brackets: [ and ]
        if '[' in text:
            open_brackets = before_text.count('[')
            close_brackets = before_text.count(']')
            if open_brackets > close_brackets:
                # We're inside [], find the next ]
                next_close = text.find(']', target_pos)
                if next_close != -1:
                    return next_close + 1

        # Position is safe
        return target_pos

    @classmethod
    def extract_and_clean(cls, text: str, format: TagFormat = TagFormat.AUTO) -> Tuple[str, List[Tag], TagFormat]:
        """
        Convenience method: extract tags and return clean text with detected format

        Args:
            text: Text containing tags
            format: Tag format (AUTO for auto-detection)

        Returns:
            Tuple of (clean_text, tags, detected_format)
        """
        if format == TagFormat.AUTO:
            format = cls.detect_format(text)

        clean_text, tags = cls.extract_tags(text, format)
        return clean_text, tags, format

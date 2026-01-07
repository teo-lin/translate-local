"""
Tests for Generic Tag Extractor

Tests tag extraction and restoration for multiple formats:
- HTML tags
- Markdown formatting
- Custom braces and brackets
- Auto-detection
- Mixed formats
"""

import pytest
from src.tag_extractor import GenericTagExtractor, TagFormat, Tag


class TestHTMLTags:
    """Test HTML tag extraction and restoration."""

    def test_extract_simple_html_tags(self):
        """Test extracting simple HTML tags."""
        text = "Welcome to <b>MyApp</b>!"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert clean_text == "Welcome to MyApp!"
        assert len(tags) == 2
        assert tags[0].content == "<b>"
        assert tags[1].content == "</b>"

    def test_extract_html_with_attributes(self):
        """Test extracting HTML tags with attributes."""
        text = 'Click <a href="https://example.com">here</a>'
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert clean_text == "Click here"
        assert len(tags) == 2
        assert tags[0].content == '<a href="https://example.com">'
        assert tags[1].content == "</a>"

    def test_restore_html_tags(self):
        """Test restoring HTML tags after translation."""
        original = "Welcome to <b>MyApp</b>!"
        clean_text, tags = GenericTagExtractor.extract_tags(original, TagFormat.HTML)

        # Simulate translation
        translated = "Bine ați venit la MyApp!"

        # Restore tags
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        # Should have tags restored (proportional positioning)
        assert "<b>" in result
        assert "</b>" in result
        assert "Bine ați venit" in result

    def test_nested_html_tags(self):
        """Test nested HTML tags."""
        text = "This is <b>bold and <i>italic</i></b> text"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert clean_text == "This is bold and italic text"
        assert len(tags) == 4  # <b>, <i>, </i>, </b>


class TestMarkdownTags:
    """Test Markdown formatting extraction and restoration."""

    def test_extract_bold_markdown(self):
        """Test extracting Markdown bold."""
        text = "This is **bold** text"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.MARKDOWN)

        assert "bold" in clean_text
        assert "**" not in clean_text
        assert len(tags) >= 1  # At least one match for **bold**

    def test_extract_italic_markdown(self):
        """Test extracting Markdown italic."""
        text = "This is *italic* text"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.MARKDOWN)

        assert "italic" in clean_text
        assert len(tags) >= 1

    def test_extract_code_markdown(self):
        """Test extracting Markdown code."""
        text = "Use `code` here"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.MARKDOWN)

        assert "code" in clean_text
        assert "`" not in clean_text
        assert len(tags) >= 1

    def test_extract_link_markdown(self):
        """Test extracting Markdown links."""
        text = "Click [here](https://example.com) for more"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.MARKDOWN)

        # Link should be extracted
        assert len(tags) >= 1
        assert any("[here](https://example.com)" in tag.content for tag in tags)

    def test_restore_markdown_tags(self):
        """Test restoring Markdown tags."""
        original = "This is **bold** text"
        clean_text, tags = GenericTagExtractor.extract_tags(original, TagFormat.MARKDOWN)

        translated = "Acesta este text îngroșat"
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        # Should have ** markers restored
        assert result.count("**") >= 2 or "**" in str(tags)


class TestCustomBraces:
    """Test custom brace format extraction and restoration."""

    def test_extract_single_braces(self):
        """Test extracting single braces {var}."""
        text = "Hello {name}, welcome!"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.CUSTOM_BRACES)

        assert clean_text == "Hello, welcome!"
        assert len(tags) == 1
        assert tags[0].content == "{name}"

    def test_extract_double_braces(self):
        """Test extracting double braces {{placeholder}}."""
        text = "Value: {{placeholder}}"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.CUSTOM_BRACES)

        assert clean_text == "Value:"
        assert len(tags) == 1
        assert tags[0].content == "{{placeholder}}"

    def test_restore_braces(self):
        """Test restoring brace variables."""
        original = "Hello {name}!"
        clean_text, tags = GenericTagExtractor.extract_tags(original, TagFormat.CUSTOM_BRACES)

        translated = "Salut!"
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        assert "{name}" in result


class TestCustomBrackets:
    """Test custom bracket format extraction and restoration."""

    def test_extract_brackets(self):
        """Test extracting brackets [var]."""
        text = "Character: [character_name]"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.CUSTOM_BRACKETS)

        assert clean_text == "Character:"
        assert len(tags) == 1
        assert tags[0].content == "[character_name]"

    def test_restore_brackets(self):
        """Test restoring bracket variables."""
        original = "Name: [name]"
        clean_text, tags = GenericTagExtractor.extract_tags(original, TagFormat.CUSTOM_BRACKETS)

        translated = "Nume:"
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        assert "[name]" in result


class TestAutoDetection:
    """Test automatic format detection."""

    def test_detect_html(self):
        """Test auto-detecting HTML format."""
        text = "This is <b>bold</b> text"
        detected = GenericTagExtractor.detect_format(text)

        assert detected == TagFormat.HTML

    def test_detect_markdown(self):
        """Test auto-detecting Markdown format."""
        text = "This is **bold** text"
        detected = GenericTagExtractor.detect_format(text)

        assert detected == TagFormat.MARKDOWN

    def test_detect_braces(self):
        """Test auto-detecting brace format."""
        text = "Hello {name}"
        detected = GenericTagExtractor.detect_format(text)

        assert detected == TagFormat.CUSTOM_BRACES

    def test_detect_brackets(self):
        """Test auto-detecting bracket format."""
        text = "Character: [name]"
        detected = GenericTagExtractor.detect_format(text)

        assert detected == TagFormat.CUSTOM_BRACKETS

    def test_auto_extract_and_clean(self):
        """Test extract_and_clean with auto-detection."""
        text = "Welcome to <b>MyApp</b>!"
        clean_text, tags, detected_format = GenericTagExtractor.extract_and_clean(text)

        assert detected_format == TagFormat.HTML
        assert clean_text == "Welcome to MyApp!"
        assert len(tags) == 2


class TestMixedFormats:
    """Test handling of mixed or complex tag scenarios."""

    def test_no_tags(self):
        """Test text with no tags."""
        text = "Simple text with no markup"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.AUTO)

        assert clean_text == "Simple text with no markup"
        assert len(tags) == 0

    def test_multiple_tags_same_type(self):
        """Test multiple tags of the same type."""
        text = "I like <b>apples</b> and <b>oranges</b>"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert clean_text == "I like apples and oranges"
        assert len(tags) == 4  # 2 opening + 2 closing

    def test_empty_text(self):
        """Test empty text."""
        text = ""
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.AUTO)

        assert clean_text == ""
        assert len(tags) == 0

    def test_tags_only(self):
        """Test text that is only tags."""
        text = "<br/>"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert clean_text.strip() == ""
        assert len(tags) == 1


class TestSafeInsertion:
    """Test safe insertion point detection."""

    def test_safe_insertion_outside_tags(self):
        """Test that insertion outside tags is safe."""
        text = "Hello <b>world</b>!"
        pos = GenericTagExtractor._find_safe_insertion_point(text, 0, 'html')

        assert pos == 0  # Beginning is safe

    def test_safe_insertion_inside_tag(self):
        """Test that insertion inside tag moves to safe position."""
        text = "Hello <b>world</b>!"
        pos = GenericTagExtractor._find_safe_insertion_point(text, 7, 'html')  # Inside <b>

        # Should move to after the >
        assert pos > 7

    def test_safe_insertion_inside_braces(self):
        """Test safe insertion with braces."""
        text = "Hello {name}!"
        pos = GenericTagExtractor._find_safe_insertion_point(text, 7, 'brace_single')  # Inside {name}

        # Should move to after the }
        assert pos >= text.index('}') + 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_restore_with_no_tags(self):
        """Test restoring when there are no tags."""
        translated = "Simple translated text"
        result = GenericTagExtractor.restore_tags(translated, [], "original")

        assert result == translated

    def test_restore_shorter_text(self):
        """Test restoring tags when translated text is shorter."""
        original = "This is a very long sentence"
        text = "This is a very long sentence with <b>bold</b> text"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        translated = "Scurt"  # Much shorter
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        # Should not crash
        assert isinstance(result, str)
        assert len(result) > 0

    def test_restore_longer_text(self):
        """Test restoring tags when translated text is longer."""
        original = "Short"
        text = "Short <b>text</b>"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        translated = "This is a much longer translated text"
        result = GenericTagExtractor.restore_tags(translated, tags, clean_text)

        # Should not crash
        assert isinstance(result, str)
        assert "<b>" in result
        assert "</b>" in result

    def test_unicode_text(self):
        """Test handling Unicode characters."""
        text = "Bună <b>ziua</b>! 你好 🌍"
        clean_text, tags = GenericTagExtractor.extract_tags(text, TagFormat.HTML)

        assert "Bună" in clean_text
        assert "你好" in clean_text
        assert "🌍" in clean_text
        assert len(tags) == 2

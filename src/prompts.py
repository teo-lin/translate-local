"""
Translation Prompts for Generic YAML Translation

This module loads prompt templates from data/ directory for easier customization.
Keeping prompts in separate files allows for easier editing, versioning, and A/B testing.

Supports multiple tag formats:
- HTML tags: <b>, <i>, <a href="...">, etc.
- Markdown: **bold**, *italic*, [link](url), `code`
- Custom variables: {var}, {{placeholder}}, [variable]
"""

from pathlib import Path

# Determine project root (go up from src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Load prompt templates once at module import
# Fallback hierarchy: translate_uncensored.txt → translate.txt → embedded template
try:
    TRANSLATION_PROMPT_TEMPLATE = (PROJECT_ROOT / "data" / "prompts" / "translate_uncensored.txt").read_text(encoding='utf-8')
except FileNotFoundError:
    try:
        TRANSLATION_PROMPT_TEMPLATE = (PROJECT_ROOT / "data" / "prompts" / "translate.txt").read_text(encoding='utf-8')
    except FileNotFoundError:
        # Fallback to embedded template if neither file exists
        TRANSLATION_PROMPT_TEMPLATE = """Translate this text to natural, colloquial {target_language}.{glossary_instructions}{context_section}{speaker_hint}

CRITICAL RULES:
1. Use natural {target_language} idioms and expressions, NOT literal word-for-word translations
2. Use appropriate formality level based on context
3. Match gender and number agreement based on context
4. Use glossary terms exactly as specified - maintain consistency
5. Follow proper {target_language} word order and grammar rules
6. **TAG PRESERVATION (CRITICAL - TAGS WILL BE REMOVED BEFORE TRANSLATION):**
   - You will receive text with tags already removed
   - Tags will be automatically restored after translation
   - Focus on translating the content, not preserving tags
7. **DO NOT TRANSLATE THESE:**
   - Proper nouns (names of people, places, brands)
   - Technical terms
   - URLs and links
   - Code snippets

GRAMMAR RULES:
8. Use correct verb conjugations and tenses for {target_language}
9. Apply proper diacritics and special characters for {target_language}
10. Ensure adjectives agree with nouns in gender/number as required

Text to translate: {text}
{target_language}:"""

# Fallback hierarchy: correct_uncensored.txt → correct.txt → embedded template
try:
    CORRECTION_PROMPT_TEMPLATE = (PROJECT_ROOT / "data" / "prompts" / "correct_uncensored.txt").read_text(encoding='utf-8')
except FileNotFoundError:
    try:
        CORRECTION_PROMPT_TEMPLATE = (PROJECT_ROOT / "data" / "prompts" / "correct.txt").read_text(encoding='utf-8')
    except FileNotFoundError:
        # Fallback to embedded template if neither file exists
        CORRECTION_PROMPT_TEMPLATE = """You are a {target_language} grammar expert. Correct ONLY the grammatical errors in this {target_language} text.

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Fix verb conjugations and tenses according to {target_language} grammar rules
2. Fix pronoun usage (reflexive, possessive, etc.) when grammatically required
3. Fix gender/number agreement (adjectives must match nouns)
4. Fix diacritics and special characters for {target_language}
5. Fix spelling errors
6. Preserve all markup tags (HTML, Markdown, variables) EXACTLY as-is

ABSOLUTE PROHIBITIONS - NEVER DO THESE:
1. NEVER change proper names (names of people, places, brands)
2. NEVER change punctuation style (keep ..., ?!?, !!, etc. exactly as written)
3. NEVER remove or add words unless fixing grammar (keep meaning 100% identical)
4. NEVER change sentence structure unless grammatically wrong
5. NEVER modify or remove markup tags: <b>, **bold**, {var}, etc.
6. NEVER change URLs, links, or code snippets
7. If text is already grammatically correct, return it UNCHANGED
8. Do NOT translate to other languages
9. Do NOT add explanations

{target_language} text to correct: {text}
Corrected {target_language}:"""


def create_translation_prompt(text: str, target_language: str = "Romanian",
                              glossary_instructions: str = "",
                              context_section: str = "", speaker_hint: str = "") -> str:
    """
    Create optimized prompt for translation with context awareness

    Args:
        text: English text to translate
        target_language: Target language name (e.g., "Romanian", "Spanish", "French")
        glossary_instructions: Optional glossary terms to enforce
        context_section: Optional previous dialogue context
        speaker_hint: Optional character/speaker identifier

    Returns:
        Complete translation prompt
    """
    return TRANSLATION_PROMPT_TEMPLATE.format(
        target_language=target_language,
        glossary_instructions=glossary_instructions,
        context_section=context_section,
        speaker_hint=speaker_hint,
        text=text
    )


def create_correction_prompt(text: str, target_language: str = "Romanian") -> str:
    """
    Create prompt for correcting grammar errors

    Args:
        text: Translated text with potential errors
        target_language: Language name (e.g., "Romanian", "Spanish", "French")

    Returns:
        Complete correction prompt
    """
    return CORRECTION_PROMPT_TEMPLATE.format(
        target_language=target_language,
        text=text
    )

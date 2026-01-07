#!/usr/bin/env python3
"""
Generic YAML Translation Script

Main entry point for translating YAML files with tag preservation.
Supports HTML, Markdown, and custom markup formats.
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import TranslationFile, TranslationBlock, FileMetadata, GenericTagInfo
from src.tag_extractor import GenericTagExtractor, TagFormat, Tag


def load_translation_file(file_path: Path) -> TranslationFile:
    """
    Load a YAML translation file.

    Args:
        file_path: Path to YAML file

    Returns:
        TranslationFile structure
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data


def save_translation_file(file_path: Path, translation_file: TranslationFile):
    """
    Save a translation file to YAML.

    Args:
        file_path: Path to output YAML file
        translation_file: TranslationFile structure
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            translation_file,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )


def identify_untranslated(
    blocks: Dict[str, TranslationBlock],
    target_lang: str
) -> List[str]:
    """
    Identify blocks that need translation for the target language.

    Args:
        blocks: Dictionary of translation blocks
        target_lang: Target language code

    Returns:
        List of block IDs that need translation
    """
    untranslated = []

    for block_id, block in blocks.items():
        translations = block.get('translations', {})
        target_text = translations.get(target_lang, '')

        # Check if translation is missing or empty
        if not target_text or not target_text.strip():
            untranslated.append(block_id)

    return untranslated


def translate_file(
    yaml_path: Path,
    target_lang: str,
    translator,
    tag_format: str = "auto",
    output_path: Optional[Path] = None
) -> Dict[str, int]:
    """
    Translate untranslated blocks in a YAML file.

    Args:
        yaml_path: Path to YAML translation file
        target_lang: Target language code (e.g., "ro", "es")
        translator: Translator backend (with .translate() method)
        tag_format: Tag format to use ("auto", "html", "markdown", etc.)
        output_path: Optional output path (default: overwrite input)

    Returns:
        Statistics dict: {'total', 'translated', 'skipped', 'failed'}
    """
    if output_path is None:
        output_path = yaml_path

    print(f"Loading translation file: {yaml_path}")

    # Load file
    translation_file = load_translation_file(yaml_path)
    metadata = translation_file.get('metadata', {})
    blocks = translation_file.get('blocks', {})

    # Convert tag format string to enum
    try:
        format_enum = TagFormat[tag_format.upper()]
    except KeyError:
        format_enum = TagFormat.AUTO

    # Identify untranslated blocks
    untranslated_ids = identify_untranslated(blocks, target_lang)
    total_blocks = len(blocks)

    print(f"Total blocks: {total_blocks}")
    print(f"Untranslated blocks: {len(untranslated_ids)}")
    print(f"Already translated: {total_blocks - len(untranslated_ids)}")

    if not untranslated_ids:
        print("\nAll blocks are already translated!")
        return {
            'total': total_blocks,
            'translated': 0,
            'skipped': total_blocks,
            'failed': 0
        }

    # Translate blocks
    print(f"\n[Starting] Translation to {target_lang}...")
    translated_count = 0
    failed_count = 0

    for idx, block_id in enumerate(untranslated_ids, start=1):
        print(f"\n[{idx}/{len(untranslated_ids)}] Translating: {block_id}")

        block = blocks[block_id]
        source_text = block.get('source_text', '')

        if not source_text:
            print(f"  Skipping: No source text")
            continue

        try:
            # Extract tags from source text
            clean_text, tags, detected_format = GenericTagExtractor.extract_and_clean(
                source_text,
                format_enum
            )

            print(f"  Source: {clean_text[:60]}...")
            if tags:
                print(f"  Tags detected: {len(tags)} ({detected_format.value})")

            # Get context and speaker
            context = block.get('context')
            speaker = block.get('speaker')

            # Prepare context list for translator
            context_list = [context] if context else None

            # Translate clean text
            translated_text = translator.translate(
                text=clean_text,
                context=context_list,
                speaker=speaker
            )

            # Restore tags in translated text
            if tags:
                translated_with_tags = GenericTagExtractor.restore_tags(
                    translated_text,
                    tags,
                    clean_text
                )
            else:
                translated_with_tags = translated_text

            # Update block
            if 'translations' not in block:
                block['translations'] = {}

            block['translations'][target_lang] = translated_with_tags
            translated_count += 1

            print(f"  Translated: {translated_with_tags[:60]}...")

        except Exception as e:
            print(f"  Translation failed: {e}")
            failed_count += 1

    # Update metadata
    metadata['updated_at'] = datetime.now().isoformat()
    if target_lang not in metadata.get('target_languages', []):
        target_languages = metadata.get('target_languages', [])
        target_languages.append(target_lang)
        metadata['target_languages'] = target_languages

    translation_file['metadata'] = metadata

    # Save updated file
    print(f"\nSaving translated file to: {output_path}")
    save_translation_file(output_path, translation_file)

    # Return statistics
    stats = {
        'total': total_blocks,
        'translated': translated_count,
        'skipped': total_blocks - len(untranslated_ids),
        'failed': failed_count
    }

    print(f"\n[Complete] Translation complete!")
    print(f"   Total blocks: {stats['total']}")
    print(f"   Translated: {stats['translated']}")
    print(f"   Already done: {stats['skipped']}")
    print(f"   Failed: {stats['failed']}")

    return stats


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Translate YAML files with tag preservation"
    )

    parser.add_argument(
        'yaml_file',
        type=Path,
        help='Path to YAML translation file'
    )

    parser.add_argument(
        '--target',
        '-t',
        required=True,
        help='Target language code (e.g., ro, es, fr)'
    )

    parser.add_argument(
        '--model',
        '-m',
        default='aya23',
        choices=['aya23', 'madlad400'],
        help='Translation model to use (default: aya23)'
    )

    parser.add_argument(
        '--tag-format',
        default='auto',
        choices=['auto', 'html', 'markdown', 'custom_braces', 'custom_brackets'],
        help='Tag format (default: auto-detect)'
    )

    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        help='Output file path (default: overwrite input)'
    )

    args = parser.parse_args()

    # Validate input file
    if not args.yaml_file.exists():
        print(f"Error: File not found: {args.yaml_file}")
        sys.exit(1)

    # Load translator
    print(f"Loading translator: {args.model}")
    if args.model == 'aya23':
        from src.translators.aya23_translator import Aya23Translator
        translator = Aya23Translator()
    elif args.model == 'madlad400':
        from src.translators.madlad400_translator import MADLAD400Translator
        translator = MADLAD400Translator()
    else:
        print(f"Error: Unknown model: {args.model}")
        sys.exit(1)

    # Translate file
    stats = translate_file(
        yaml_path=args.yaml_file,
        target_lang=args.target,
        translator=translator,
        tag_format=args.tag_format,
        output_path=args.output
    )

    sys.exit(0 if stats['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

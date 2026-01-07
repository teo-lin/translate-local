# Migration Guide: Renpy Translator → Generic YAML Translator

This guide helps you migrate from the old Ren'Py-specific translation system to the new generic YAML translator.

## What Changed?

### Major Changes

1. **Removed Renpy-Specific Code** (~1900 lines, 35% of codebase)
   - `src/renpy_utils.py` - Renpy tag and block parsing
   - `src/extract.py` - Renpy .rpy file extraction
   - `src/merge.py` - Renpy .rpy file reconstruction
   - `2-extract.ps1` - Extract phase launcher
   - `5-merge.ps1` - Merge phase launcher

2. **New Generic Tag System**
   - `src/tag_extractor.py` - Universal tag handling
   - Supports HTML, Markdown, custom markup
   - Auto-detection of tag formats

3. **Simplified Workflow**
   - **Old**: Extract → Translate → Merge (3 phases)
   - **New**: YAML → Translate → YAML (1 phase)

4. **New Entry Points**
   - `translate.ps1` - Main translation launcher
   - `scripts/translate_yaml.py` - YAML translation script

### What Was Kept?

- ✅ Translation backends (Aya-23-8B, MADLAD-400, etc.)
- ✅ Context-aware translation
- ✅ Glossary support
- ✅ Grammar correction (`4-correct.ps1`)
- ✅ Quality benchmarking (`9-benchmark.ps1`)
- ✅ Model comparison tools
- ✅ GPU acceleration

## Migration Options

### Option 1: Use Old Version (Recommended for Renpy Projects)

If you need Renpy-specific functionality:

1. **Stay on the last Renpy-compatible version**:
   ```bash
   git checkout <last-renpy-tag>
   ```

2. **Or clone the old version separately**:
   ```bash
   git clone https://github.com/your-repo/renpy-translator.git renpy-translator-old
   cd renpy-translator-old
   git checkout <last-renpy-tag>
   ```

3. Continue using the old 3-phase workflow for Renpy projects

### Option 2: Manual Migration to Generic YAML

If you want to use the new generic system with your Renpy content:

#### Step 1: Extract Final Translations from Renpy

Using the old version, extract your completed translations:

```powershell
# In old version
.\2-extract.ps1  # Extract to .parsed.yaml
```

#### Step 2: Convert to New YAML Format

Create a conversion script or manually convert `.parsed.yaml` to the new format:

**Old Format** (`.parsed.yaml`):
```yaml
1-Jasmine:
  en: "Hello, how are you?"
  ro: "Salut, ce mai faci?"

2-Player:
  en: "I'm fine, thanks!"
  ro: "Sunt bine, mulțumesc!"
```

**New Format** (`translation.yaml`):
```yaml
metadata:
  source_language: en
  target_languages: [ro]
  tag_format: custom_braces
  created_at: "2026-01-05T19:00:00"

blocks:
  dialogue-1-jasmine:
    source_text: "Hello, how are you?"
    translations:
      ro: "Salut, ce mai faci?"
    category: dialogue
    speaker: Jasmine

  dialogue-2-player:
    source_text: "I'm fine, thanks!"
    translations:
      ro: "Sunt bine, mulțumesc!"
    category: dialogue
    speaker: Player
```

#### Step 3: Update Tag Format

Renpy tags `{color=...}`, `[variables]` are handled as custom format:

```yaml
metadata:
  tag_format: custom_braces  # For {tags}
  # or
  tag_format: custom_brackets  # For [tags]
  # or
  tag_format: auto  # Auto-detect both
```

#### Step 4: Translate New Content

```powershell
.\translate.ps1 translation.yaml -Target ro
```

## File Location Changes

### Old Locations → New Locations

```
OLD: data/ro_glossary.yaml
NEW: data/examples/ro_glossary.yaml

OLD: data/ro_benchmark.yaml
NEW: data/examples/ro_benchmark.yaml

OLD: games/MyGame/
NEW: games/examples/MyGame/
```

### Deleted Files

These files no longer exist:

```
src/renpy_utils.py          # Renpy-specific utilities
src/extract.py              # Renpy extraction
src/merge.py                # Renpy merge
2-extract.ps1               # Extract launcher
5-merge.ps1                 # Merge launcher
renpy/tools_config.yaml     # Renpy SDK config
tests/test_unit_extract.py  # Extract tests
tests/test_unit_merge.py    # Merge tests
tests/test_unit_renpy_tags.py  # Renpy tag tests
```

### New Files

```
src/tag_extractor.py           # Generic tag system
scripts/translate_yaml.py      # YAML translation
translate.ps1                  # Main launcher
tests/test_generic_tags.py     # Generic tag tests
data/examples/translation_template.yaml
data/examples/html_example.yaml
data/examples/markdown_example.yaml
data/examples/custom_variables_example.yaml
data/examples/README.md
MIGRATION.md (this file)
```

## Workflow Comparison

### Old Workflow (Renpy-Specific) - REMOVED

```powershell
# 1. Configure game
.\1-config.ps1

# 2. Extract from .rpy files
.\2-extract.ps1  # DELETED
# Creates: .parsed.yaml (translations) + .tags.yaml (metadata)

# 3. Translate
.\3-translate.ps1  # DELETED
# Updates: .parsed.yaml with translations

# 4. Optional: Correct
.\4-correct.ps1  # DELETED

# 5. Merge back to .rpy
.\5-merge.ps1  # DELETED
# Creates: Updated .rpy files with translations
```

**Note**: All Renpy-specific scripts have been removed. If you need the old workflow, use a git commit before the refactor (e.g., git tag `renpy-final` if available).

### New Workflow (Generic)

```powershell
# 1. Create YAML file (one-time)
cp data/examples/translation_template.yaml translations/myapp.yaml
# Edit myapp.yaml with your content

# 2. Translate
.\translate.ps1 translations/myapp.yaml -Target ro

# Done! Translations are in the same YAML file
```

## Use Case Guide

### "I'm translating a Renpy visual novel"

**Recommendation**: Use a pre-refactor git commit

The Renpy-specific workflow has been completely removed from this version. If you need Renpy functionality:
1. Find the last commit before the refactor (look for "delete everything renpy related" in git log)
2. Checkout that commit: `git checkout <commit-hash>`
3. Alternatively, manually extract translations from .rpy files into YAML format and use the new generic translator

The old 3-phase workflow (extract → translate → merge) is no longer available.

### "I need to translate web app UI"

**Recommendation**: Use the new generic system

```yaml
# translations/webapp.yaml
metadata:
  source_language: en
  target_languages: [ro, es, fr]
  tag_format: html

blocks:
  nav-home:
    source_text: "<a href='/'>Home</a>"
    translations:
      ro: ""
      es: ""
      fr: ""
```

### "I'm translating documentation"

**Recommendation**: Use the new generic system with Markdown

```yaml
# translations/docs.yaml
metadata:
  source_language: en
  target_languages: [ro]
  tag_format: markdown

blocks:
  install-guide:
    source_text: "Run `npm install` for **all** dependencies"
    translations:
      ro: ""
```

### "I have mixed content (HTML + variables)"

**Recommendation**: Use the new generic system with auto-detection

```yaml
metadata:
  tag_format: auto  # Automatically handles mixed formats
```

## Breaking Changes

### 1. File Format

**Old**: Separate `.parsed.yaml` and `.tags.yaml` files
**New**: Single YAML file with metadata and blocks

### 2. Script Names

**Old**: `3-translate.ps1` (phase 3 of pipeline)
**New**: `translate.ps1` (standalone)

### 3. Tag Handling

**Old**: Renpy-specific `RenpyTagExtractor`
**New**: Generic `GenericTagExtractor` with format detection

### 4. Models Structure

**Old**:
```python
ParsedBlock = TypedDict with 'en', 'ro', 'type'
TaggedBlock = Renpy-specific metadata
```

**New**:
```python
TranslationBlock = Generic with 'source_text', 'translations', 'category', 'speaker', 'context'
```

## Troubleshooting Migration Issues

### Issue: "Can't find my old translations"

**Solution**: Old translations are in `.parsed.yaml` files. Either:
- Stay on old version and continue using them
- Convert to new format manually or with a script

### Issue: "Renpy tags not preserved"

**Solution**: Use `tag_format: custom_braces` or `tag_format: auto`

```yaml
metadata:
  tag_format: custom_braces  # Handles {color=#fff}, {size=+10}, etc.
```

### Issue: "Want to use both systems"

**Solution**: Keep separate directories:

```bash
project/
  renpy-translator/    # Old version (git checkout old-tag)
  yaml-translator/     # New version (latest)
```

## Getting Help

1. Check `README.md` for new system documentation
2. See `data/examples/` for YAML templates
3. Old Renpy examples are in `data/examples/` (preserved for reference)
4. Report issues on GitHub

## Summary

| Aspect | Old (Renpy) | New (Generic) |
|--------|-------------|---------------|
| **Use Case** | Renpy visual novels | Any YAML content |
| **Workflow** | 3-phase (Extract→Translate→Merge) | 1-phase (YAML→YAML) |
| **Tag Support** | Renpy tags only | HTML, Markdown, custom |
| **File Format** | `.rpy` + `.parsed.yaml` + `.tags.yaml` | Single `.yaml` file |
| **Complexity** | Higher (game-specific) | Lower (universal) |
| **Recommended For** | Renpy games | Web apps, docs, general use |

## Final Recommendation

- **For Renpy projects**: Stay on the old version (use git tag)
- **For new projects**: Use the new generic system
- **For mixed**: Keep both versions in separate directories

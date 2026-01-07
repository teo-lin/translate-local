# Translation Examples

This directory contains example translation files and legacy Renpy-era data for reference.

## Generic YAML Examples

These files demonstrate the new generic YAML translation format:

### Template Files

- **translation_template.yaml** - Complete template showing all features
- **html_example.yaml** - HTML tag preservation examples
- **markdown_example.yaml** - Markdown formatting examples
- **custom_variables_example.yaml** - Custom variable placeholders

### Using the Examples

1. Copy a template file:
   ```bash
   cp data/examples/translation_template.yaml translations/myapp.yaml
   ```

2. Edit the YAML file with your content

3. Translate using the launcher:
   ```bash
   .\translate.ps1 translations/myapp.yaml -Target ro
   ```

## YAML Format Structure

```yaml
metadata:
  source_language: en
  target_languages: [ro, es, fr]
  tag_format: auto  # auto, html, markdown, custom_braces, custom_brackets

blocks:
  block-id:
    source_text: "Original text with <tags>"
    translations:
      ro: ""  # Filled by translator
      es: ""
    category: ui  # Optional: ui, dialogue, narration, menu, etc.
    speaker: "Character Name"  # Optional: for dialogue
    context: "Additional context"  # Optional: helps translation
```

## Tag Formats

### HTML Tags
```yaml
source_text: "Welcome to <b>MyApp</b>!"
```

### Markdown
```yaml
source_text: "This is **bold** and *italic* text"
```

### Custom Variables
```yaml
source_text: "Hello {username}, you have {{count}} messages"
```

### Mixed Content
The `auto` tag format detects and handles mixed markup automatically.

## Legacy Renpy Files

The following files are from the original Renpy translation system and are kept for reference:

- **ro_glossary.yaml** - Romanian glossary (Renpy-specific)
- **ro_benchmark.yaml** - Romanian benchmark translations (Renpy-specific)
- **ro_corrections.json** - Romanian corrections database (Renpy-specific)

These files are **NOT compatible** with the new generic YAML translator. They are preserved as examples of the previous system.

### For Former Renpy Users

If you were using the Renpy-specific version of this tool:

1. See `MIGRATION.md` in the root directory for migration guidance
2. The old Renpy functionality was removed in the refactor
3. Use an older git tag if you need Renpy-specific features
4. Renpy game files (if any) are in `games/examples/`

## Creating Your Own Translation Files

### Quick Start

1. **Choose a template** based on your content type:
   - Web/app UI → `html_example.yaml`
   - Documentation → `markdown_example.yaml`
   - Dynamic content → `custom_variables_example.yaml`
   - General → `translation_template.yaml`

2. **Copy and customize**:
   ```bash
   cp data/examples/html_example.yaml translations/my-app.yaml
   ```

3. **Edit the YAML**:
   - Update `metadata` section with your languages
   - Replace example blocks with your content
   - Add/remove blocks as needed

4. **Translate**:
   ```bash
   .\translate.ps1 translations/my-app.yaml -Target ro -Model aya23
   ```

### Best Practices

- **Use meaningful block IDs**: `ui-login-button` instead of `block1`
- **Add context**: Helps the AI translator understand nuance
- **Specify speakers**: For dialogue, always include speaker name
- **Choose correct tag format**: Use `auto` if unsure
- **Keep blocks focused**: One conceptual unit per block

### Supported Languages

The translators support 400+ languages. Common codes:

- `ro` - Romanian
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `zh` - Chinese
- `ja` - Japanese
- `ar` - Arabic

See translator documentation for the full list.

## Questions or Issues?

- Check the main `README.md` for general documentation
- See `MIGRATION.md` for upgrade guidance
- Report issues on GitHub

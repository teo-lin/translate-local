# Generic YAML Translation Tool

Translate text between **400+ languages** using state-of-the-art local AI models. Automatically preserves HTML, Markdown, and custom markup during translation.

## Features

- **YAML-Based Workflow** - Simple, human-readable format for managing translations
- **Tag Preservation** - Automatically preserves HTML tags, Markdown formatting, and custom markup
- **Multiple AI Models** - Choose between Aya-23-8B (23 languages, higher quality) and MADLAD-400 (400+ languages)
- **Local Translation** - No cloud services, complete privacy
- **Context-Aware** - Use dialogue context and speaker information for better translations
- **Glossary Support** - Maintain consistent terminology across translations
- **GPU Accelerated** - Fast translation with CUDA support (6GB+ VRAM recommended)
- **Fully Offline** - All processing happens locally on your machine

## Supported Tag Formats

- **HTML**: `<b>`, `<i>`, `<a href="...">`, `<span style="...">`, etc.
- **Markdown**: `**bold**`, `*italic*`, `[link](url)`, `` `code` ``
- **Custom Variables**: `{name}`, `{{placeholder}}`, `[variable]`
- **Auto-Detection**: Automatically detects and handles mixed formats

## Quick Start

### 1. Setup (One-Time)

Run the automated setup script to download models and set up the environment:

```powershell
.\0-setup.ps1
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Download the selected AI translation model(s)
- Configure CUDA for GPU acceleration

### 2. Create a Translation File

Create a YAML file with your content. See `data/examples/` for templates:

```yaml
metadata:
  source_language: en
  target_languages: [ro, es, fr]
  tag_format: auto

blocks:
  ui-welcome:
    source_text: "Welcome to <b>MyApp</b>!"
    translations:
      ro: ""  # Will be filled by translator
      es: ""
      fr: ""
    category: ui

  dialogue-intro:
    source_text: "Hello! How are you today?"
    translations:
      ro: ""
    category: dialogue
    speaker: Sarah
    context: "First greeting from main character"
```

### 3. Translate

Run the translation script:

```powershell
# Interactive mode (recommended for first use)
.\translate.ps1 -Interactive

# Direct translation
.\translate.ps1 myfile.yaml -Target ro

# Use specific model
.\translate.ps1 myfile.yaml -Target es -Model madlad400

# Specify tag format
.\translate.ps1 myfile.yaml -Target fr -TagFormat html
```

## YAML File Format

### Metadata Section

```yaml
metadata:
  source_language: en           # Source language code
  target_languages: [ro, es]    # Target language codes
  tag_format: auto              # Tag format: auto, html, markdown, custom_braces, custom_brackets
  created_at: "2026-01-05T19:00:00"
  updated_at: "2026-01-05T19:00:00"
```

### Translation Blocks

```yaml
blocks:
  block-id:                     # Unique identifier for this block
    source_text: "Original text with <tags>"
    translations:
      ro: "Translated text"     # Translations for each language
      es: ""                    # Empty = needs translation
    category: ui                # Optional: ui, dialogue, narration, menu, etc.
    speaker: "Character Name"   # Optional: for dialogue
    context: "Additional info"  # Optional: helps translation quality
```

## Usage Examples

### Web Application UI

```yaml
blocks:
  login-button:
    source_text: "Click <a href='/login'>here</a> to sign in"
    translations:
      ro: ""
    category: ui
```

### Documentation

```yaml
blocks:
  install-guide:
    source_text: "Run `npm install` to install **all** dependencies"
    translations:
      ro: ""
    category: docs
    context: "Installation instructions"
```

### Dynamic Content

```yaml
blocks:
  user-greeting:
    source_text: "Welcome back, {username}! You have {count} messages."
    translations:
      ro: ""
    category: system
```

## Available Models

### Aya-23-8B (Recommended)
- **Languages**: 23 languages (major languages)
- **Quality**: Higher quality translations
- **Speed**: Moderate
- **VRAM**: 6GB+ recommended
- **Best for**: Quality-focused projects, major languages

### MADLAD-400-3B
- **Languages**: 400+ languages (including rare languages)
- **Quality**: Good quality
- **Speed**: Faster
- **VRAM**: 4GB+ recommended
- **Best for**: Wide language coverage, faster processing

## Command-Line Options

```powershell
# Show help
.\translate.ps1 -Help

# Interactive mode
.\translate.ps1 -Interactive

# Translate specific file
.\translate.ps1 <file.yaml> -Target <lang>

# Options:
#   -Target <lang>        Target language code (required)
#   -Model <name>         aya23 or madlad400 (default: aya23)
#   -TagFormat <format>   auto, html, markdown, custom_braces, custom_brackets (default: auto)
#   -Output <file>        Output file path (default: overwrite input)
```

## Language Codes

Common language codes:

- `en` - English
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

See model documentation for the complete list of supported languages.

## Advanced Features

### Glossary Support

Create a glossary YAML file to maintain consistent terminology:

```yaml
terms:
  - source: "account"
    target: "cont"
  - source: "settings"
    target: "setări"
```

Use with:
```powershell
python scripts/translate_yaml.py myfile.yaml --target ro --glossary my_glossary.yaml
```

### Quality Benchmarking

Compare translation quality using BLEU scores:

```powershell
.\9-benchmark.ps1 data/examples/ro_benchmark.yaml
```

## System Requirements

- **OS**: Windows 10/11, Linux, or macOS
- **GPU**: NVIDIA GPU with 6GB+ VRAM (CUDA 12.4)
  - Tested with RTX 3060
  - CPU-only mode available but slower
- **RAM**: 8GB+ system RAM recommended
- **Storage**: 10GB+ free space for models

## Directory Structure

```
├── translate.ps1           # Main translation launcher
├── 0-setup.ps1            # Setup script
├── data/
│   └── examples/          # Example YAML files and templates
├── translations/          # Your translation files (create this)
├── scripts/              # Python scripts
├── src/                  # Source code
│   ├── tag_extractor.py  # Generic tag handling
│   ├── models.py         # Data structures
│   └── translators/      # Translation backends
└── tests/                # Test suite
```

## Troubleshooting

### GPU Not Detected

Ensure CUDA 12.4 is installed and PATH is configured:
```powershell
nvidia-smi  # Check GPU status
```

### Out of Memory

- Use a smaller model (MADLAD-400)
- Reduce batch size
- Close other GPU-using applications

### Translation Quality Issues

- Add more context to blocks
- Use glossary for consistent terminology
- Specify speaker for dialogue
- Try the Aya-23-8B model for better quality

## Migration from Renpy Version

This tool was originally built for Ren'Py visual novel translation. If you're migrating from the old Renpy-specific version:

1. See `MIGRATION.md` for detailed migration guide
2. Example Renpy files are in `data/examples/` and `games/examples/`
3. Old Renpy-specific code was removed - use an older git tag if needed

## Examples and Templates

See `data/examples/` for:

- `translation_template.yaml` - Complete feature template
- `html_example.yaml` - HTML tag preservation
- `markdown_example.yaml` - Markdown formatting
- `custom_variables_example.yaml` - Variable placeholders

## Contributing

Issues and pull requests welcome on GitHub.

## License

See LICENSE file for details.

## Acknowledgments

- Built with PyTorch and Hugging Face Transformers
- Uses Aya-23-8B and MADLAD-400 models
- Original Renpy version developed for visual novel translation

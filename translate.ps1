# Generic YAML Translation Launcher
# Translates YAML files with tag preservation (HTML, Markdown, custom markup)
# Simple replacement for the 3-phase Renpy pipeline

param(
    [string]$YamlFile = "",       # YAML file to translate
    [string]$Target = "",         # Target language code (e.g., ro, es, fr)
    [string]$Model = "aya23",     # Translation model (aya23 or madlad400)
    [string]$TagFormat = "auto",  # Tag format (auto, html, markdown, custom_braces, custom_brackets)
    [string]$Output = "",         # Optional output file (default: overwrite input)
    [switch]$Interactive,         # Interactive mode: list and select YAML files
    [switch]$Help                 # Show help
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Help) {
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "       Generic YAML Translation Tool - Help                     " -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Translate YAML files with automatic tag preservation."
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\translate.ps1 -Interactive                    # Interactive mode"
    Write-Host "  .\translate.ps1 file.yaml -Target ro            # Translate to Romanian"
    Write-Host "  .\translate.ps1 file.yaml -Target es -Model madlad400  # Use MADLAD model"
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -YamlFile <path>      YAML file to translate"
    Write-Host "  -Target <lang>        Target language code (e.g., ro, es, fr)"
    Write-Host "  -Model <name>         Translation model: aya23 (default) or madlad400"
    Write-Host "  -TagFormat <format>   Tag format: auto (default), html, markdown, custom_braces, custom_brackets"
    Write-Host "  -Output <path>        Output file (default: overwrite input)"
    Write-Host "  -Interactive          Interactive mode - list available YAML files"
    Write-Host "  -Help                 Show this help"
    Write-Host ""
    Write-Host "TAG FORMATS:" -ForegroundColor Yellow
    Write-Host "  auto              Auto-detect format from content (recommended)"
    Write-Host "  html              HTML tags: <b>, <tag attr='value'>, etc."
    Write-Host "  markdown          Markdown: **bold**, *italic*, [link](url), \`code\`"
    Write-Host "  custom_braces     Custom braces: {var}, {{placeholder}}"
    Write-Host "  custom_brackets   Custom brackets: [var]"
    Write-Host ""
    Write-Host "YAML FORMAT:" -ForegroundColor Yellow
    Write-Host "  metadata:"
    Write-Host "    source_language: en"
    Write-Host "    target_languages: [ro, es]"
    Write-Host "  blocks:"
    Write-Host "    ui-welcome:"
    Write-Host "      source_text: 'Welcome to <b>MyApp</b>!'"
    Write-Host "      translations:"
    Write-Host "        ro: ''  # Will be filled by translator"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  See data/examples/ for example YAML files"
    Write-Host ""
    exit 0
}

$pythonExe = Join-Path $scriptDir "venv\Scripts\python.exe"
$pythonScript = Join-Path $scriptDir "scripts\translate_yaml.py"

# Verify Python executable exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "Error: Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run .\0-setup.ps1 first to set up the environment." -ForegroundColor Yellow
    exit 1
}

# Add PyTorch lib directory to PATH for CUDA DLLs
$torchLibPath = Join-Path $scriptDir "venv\Lib\site-packages\torch\lib"
if (Test-Path $torchLibPath) {
    $env:PATH = "$torchLibPath;$env:PATH"
}

# Interactive mode: list YAML files in translations directory
if ($Interactive) {
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host "       Interactive Translation Mode                             " -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host ""

    # Look for YAML files in common locations
    $searchDirs = @(
        (Join-Path $scriptDir "translations"),
        (Join-Path $scriptDir "data"),
        $scriptDir
    )

    $yamlFiles = @()
    foreach ($dir in $searchDirs) {
        if (Test-Path $dir) {
            $yamlFiles += Get-ChildItem -Path $dir -Filter "*.yaml" -Recurse | Select-Object -ExpandProperty FullName
            $yamlFiles += Get-ChildItem -Path $dir -Filter "*.yml" -Recurse | Select-Object -ExpandProperty FullName
        }
    }

    if ($yamlFiles.Count -eq 0) {
        Write-Host "No YAML files found in:" -ForegroundColor Yellow
        foreach ($dir in $searchDirs) {
            Write-Host "  - $dir"
        }
        Write-Host ""
        Write-Host "Please create a YAML file first. See data/examples/ for templates." -ForegroundColor Yellow
        exit 1
    }

    # Display files
    Write-Host "Available YAML files:" -ForegroundColor Green
    for ($i = 0; $i -lt $yamlFiles.Count; $i++) {
        $relativePath = $yamlFiles[$i].Replace($scriptDir, "").TrimStart("\")
        Write-Host "  [$($i + 1)] $relativePath"
    }
    Write-Host ""

    # Select file
    $selection = Read-Host "Select file number (1-$($yamlFiles.Count))"
    try {
        $selectedIndex = [int]$selection - 1
        if ($selectedIndex -lt 0 -or $selectedIndex -ge $yamlFiles.Count) {
            Write-Host "Invalid selection!" -ForegroundColor Red
            exit 1
        }
        $YamlFile = $yamlFiles[$selectedIndex]
    } catch {
        Write-Host "Invalid input!" -ForegroundColor Red
        exit 1
    }

    # Get target language
    Write-Host ""
    Write-Host "Common language codes:" -ForegroundColor Green
    Write-Host "  ro - Romanian   es - Spanish    fr - French"
    Write-Host "  de - German     it - Italian    pt - Portuguese"
    Write-Host "  ru - Russian    tr - Turkish    pl - Polish"
    Write-Host ""
    $Target = Read-Host "Enter target language code"

    # Get model
    Write-Host ""
    Write-Host "Available models:" -ForegroundColor Green
    Write-Host "  [1] aya23 (recommended, better quality)"
    Write-Host "  [2] madlad400 (faster, supports more languages)"
    Write-Host ""
    $modelChoice = Read-Host "Select model (1-2, default: 1)"
    if ($modelChoice -eq "2") {
        $Model = "madlad400"
    } else {
        $Model = "aya23"
    }
}

# Validate required parameters
if (-not $YamlFile) {
    Write-Host "Error: YAML file not specified!" -ForegroundColor Red
    Write-Host "Use -Interactive mode or specify -YamlFile parameter" -ForegroundColor Yellow
    Write-Host "Run .\translate.ps1 -Help for more information" -ForegroundColor Yellow
    exit 1
}

if (-not $Target) {
    Write-Host "Error: Target language not specified!" -ForegroundColor Red
    Write-Host "Use -Target parameter (e.g., -Target ro)" -ForegroundColor Yellow
    exit 1
}

# Verify input file exists
if (-not (Test-Path $YamlFile)) {
    Write-Host "Error: File not found: $YamlFile" -ForegroundColor Red
    exit 1
}

# Build command
$args = @(
    $pythonScript,
    $YamlFile,
    "--target", $Target,
    "--model", $Model,
    "--tag-format", $TagFormat
)

if ($Output) {
    $args += @("--output", $Output)
}

# Display configuration
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "       Translation Configuration                                " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Input file:   $YamlFile" -ForegroundColor White
Write-Host "  Target lang:  $Target" -ForegroundColor White
Write-Host "  Model:        $Model" -ForegroundColor White
Write-Host "  Tag format:   $TagFormat" -ForegroundColor White
if ($Output) {
    Write-Host "  Output file:  $Output" -ForegroundColor White
} else {
    Write-Host "  Output file:  (overwrite input)" -ForegroundColor White
}
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Execute translation
try {
    & $pythonExe @args

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=================================================================" -ForegroundColor Green
        Write-Host "       Translation Successful!                                  " -ForegroundColor Green
        Write-Host "=================================================================" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Translation completed with errors (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
        Write-Host ""
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Red
    Write-Host "       Translation Failed                                       " -ForegroundColor Red
    Write-Host "=================================================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}

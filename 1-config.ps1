# Configuration Script for Generic YAML Translator
# Sets default model and language preferences

param(
    [string]$Language = "",
    [string]$Model = "",
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Help) {
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "       Configuration - Help                                     " -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configure default model and language for translation."
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\1-config.ps1                 # Interactive mode"
    Write-Host "  .\1-config.ps1 -Language ro -Model aya23"
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -Language <code>   Default language code (e.g., ro, es, fr)"
    Write-Host "  -Model <name>      Default model: aya23 or madlad400"
    Write-Host "  -Help              Show this help"
    Write-Host ""
    Write-Host "NOTE:" -ForegroundColor Yellow
    Write-Host "  This configuration is optional. You can always specify"
    Write-Host "  language and model directly in the translate.ps1 command."
    Write-Host ""
    exit 0
}

# Get Python executable from virtual environment
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run .\0-setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Config file path
$configFile = Join-Path $scriptDir "models\current_config.yaml"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "       Configuration                                             " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Load existing config if it exists
$existingConfig = @{}
if (Test-Path $configFile) {
    try {
        $yamlContent = Get-Content $configFile -Raw
        # Basic YAML parsing for PowerShell
        $yamlLines = $yamlContent -split "`n"
        foreach ($line in $yamlLines) {
            if ($line -match '^\s*default_language:\s*(.+)') {
                $existingConfig['language'] = $matches[1].Trim()
            }
            if ($line -match '^\s*default_model:\s*(.+)') {
                $existingConfig['model'] = $matches[1].Trim()
            }
        }
    } catch {
        Write-Host "Warning: Could not parse existing config" -ForegroundColor Yellow
    }
}

# Interactive mode if no parameters provided
if (-not $Language -and -not $Model) {
    Write-Host "Current configuration:" -ForegroundColor Green
    if ($existingConfig.ContainsKey('language')) {
        Write-Host "  Language: $($existingConfig['language'])"
    } else {
        Write-Host "  Language: (not set)"
    }
    if ($existingConfig.ContainsKey('model')) {
        Write-Host "  Model: $($existingConfig['model'])"
    } else {
        Write-Host "  Model: (not set)"
    }
    Write-Host ""

    # Ask for language
    Write-Host "Common language codes:" -ForegroundColor Green
    Write-Host "  ro - Romanian   es - Spanish    fr - French"
    Write-Host "  de - German     it - Italian    pt - Portuguese"
    Write-Host "  ru - Russian    tr - Turkish    pl - Polish"
    Write-Host ""
    $Language = Read-Host "Enter default language code (or press Enter to keep current)"

    if ($Language -eq "" -and $existingConfig.ContainsKey('language')) {
        $Language = $existingConfig['language']
    }

    # Ask for model
    Write-Host ""
    Write-Host "Available models:" -ForegroundColor Green
    Write-Host "  [1] aya23 (recommended, better quality, 23 languages)"
    Write-Host "  [2] madlad400 (faster, 400+ languages)"
    Write-Host ""
    $modelChoice = Read-Host "Select model (1-2, or press Enter to keep current)"

    if ($modelChoice -eq "1") {
        $Model = "aya23"
    } elseif ($modelChoice -eq "2") {
        $Model = "madlad400"
    } elseif ($modelChoice -eq "" -and $existingConfig.ContainsKey('model')) {
        $Model = $existingConfig['model']
    } else {
        $Model = "aya23"  # Default
    }
}

# Validate inputs
if (-not $Language) {
    Write-Host "ERROR: Language not specified!" -ForegroundColor Red
    exit 1
}

if (-not $Model) {
    $Model = "aya23"  # Default
}

# Create config content
$configContent = @"
# Generic YAML Translator Configuration
# This file stores default preferences for translation

default_language: $Language
default_model: $Model

# Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

# Ensure models directory exists
$modelsDir = Join-Path $scriptDir "models"
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
}

# Save configuration
$configContent | Out-File -FilePath $configFile -Encoding utf8 -Force

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "       Configuration Saved!                                     " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "  Default language: $Language" -ForegroundColor White
Write-Host "  Default model:    $Model" -ForegroundColor White
Write-Host ""
Write-Host "You can now use .\translate.ps1 with these defaults." -ForegroundColor White
Write-Host "Or override them by specifying -Target and -Model parameters." -ForegroundColor White
Write-Host ""

# Script to convert all text files to UTF-8 encoding
# Run this script to ensure all files in the project use UTF-8

Write-Host "Converting files to UTF-8 encoding..." -ForegroundColor Cyan

$filePatterns = @('*.py', '*.txt', '*.md', '*.yml', '*.yaml', '*.json', '*.sh', '*.bicep', '*.html')
$filesConverted = 0
$filesSkipped = 0

foreach ($pattern in $filePatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -Recurse -File | Where-Object {
        $_.FullName -notmatch '\\venv\\' -and 
        $_.FullName -notmatch '\\\.git\\' -and
        $_.FullName -notmatch '\\__pycache__\\' -and
        $_.FullName -notmatch '\\node_modules\\'
    }
    
    foreach ($file in $files) {
        try {
            # Read file content
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            
            if ($null -ne $content) {
                # Write back as UTF-8 without BOM
                $utf8NoBom = New-Object System.Text.UTF8Encoding $false
                [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBom)
                
                Write-Host "  [OK] $($file.FullName)" -ForegroundColor Green
                $filesConverted++
            }
        }
        catch {
            Write-Host "  [SKIP] $($file.FullName) - $($_.Exception.Message)" -ForegroundColor Yellow
            $filesSkipped++
        }
    }
}

Write-Host "`nConversion complete!" -ForegroundColor Cyan
Write-Host "  Files converted: $filesConverted" -ForegroundColor Green
Write-Host "  Files skipped: $filesSkipped" -ForegroundColor Yellow

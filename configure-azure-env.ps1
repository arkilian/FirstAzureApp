<#
Script: configure-azure-env.ps1
Purpose: Configure database environment variables in Azure App Service without hardcoding secrets.

Usage examples:
    # Load from current shell environment (recommended)
    .\configure-azure-env.ps1

    # Or pass values explicitly (password will be prompted if omitted)
    .\configure-azure-env.ps1 -DbHost "host" -DbName "db" -DbUser "user" -DbPort 5432

    # Or import from .env first in PowerShell session
    Get-Content .env | Where-Object {$_ -and -not $_.StartsWith('#')} | ForEach-Object { $k,$v = $_.Split('=',2); Set-Item -Path Env:\$k -Value $v }
    .\configure-azure-env.ps1
#>

[CmdletBinding()]
param(
    [string]$DbHost = $env:DB_HOST,
    [string]$DbName = $env:DB_NAME,
    [string]$DbUser = $env:DB_USER,
    [string]$DbPassword = $env:DB_PASSWORD,
    [int]$DbPort = $(if ($env:DB_PORT) { [int]$env:DB_PORT } else { 5432 }),
    [ValidateSet('production','development','staging')]
    [string]$FlaskEnv = $(if ($env:FLASK_ENV) { $env:FLASK_ENV } else { 'production' }),
    [bool]$FlaskDebug = $(if ($env:FLASK_DEBUG) { $env:FLASK_DEBUG -in @('1','true','True') } else { $false })
)

Write-Host "Configuring App Service application settings (no secrets printed)..." -ForegroundColor Cyan

# Get the web app name from azd
$webUri = azd env get-value WEB_URI
if (-not $webUri) { throw "WEB_URI not found in azd environment. Run 'azd env get-values' to verify." }
$webAppName = ($webUri -replace '^https://', '' -replace '\.azurewebsites\.net/?$', '')

# Resolve resource group
$resourceGroup = az webapp list --query "[?name=='$webAppName'].resourceGroup" -o tsv
if (-not $resourceGroup) { throw "Could not resolve resource group for web app '$webAppName'" }

# Prompt for password if not provided
if (-not $DbPassword) {
    $secure = Read-Host -AsSecureString -Prompt "Enter DB_PASSWORD"
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { $DbPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

# Validate required inputs
$missing = @()
if (-not $DbHost) { $missing += 'DB_HOST' }
if (-not $DbName) { $missing += 'DB_NAME' }
if (-not $DbUser) { $missing += 'DB_USER' }
if (-not $DbPassword) { $missing += 'DB_PASSWORD' }
if ($missing.Count -gt 0) { throw "Missing required values: $($missing -join ', ')" }

Write-Host "Web App: $webAppName" -ForegroundColor Yellow
Write-Host "Resource Group: $resourceGroup" -ForegroundColor Yellow
Write-Host "Setting application settings (values hidden)..." -ForegroundColor Cyan

# Prepare settings; never print secret values
$settings = @{
    "DB_HOST" = $DbHost
    "DB_NAME" = $DbName
    "DB_USER" = $DbUser
    "DB_PASSWORD" = $DbPassword
    "DB_PORT" = "$DbPort"
    "FLASK_ENV" = $FlaskEnv
    "FLASK_DEBUG" = $(if ($FlaskDebug) { 'True' } else { 'False' })
}

foreach ($k in $settings.Keys) {
    Write-Host "  Setting $k" -ForegroundColor Gray
    az webapp config appsettings set --name $webAppName --resource-group $resourceGroup --settings "$k=$($settings[$k])" --output none
}

Write-Host "Restarting web app..." -ForegroundColor Cyan
az webapp restart --name $webAppName --resource-group $resourceGroup --output none
Write-Host "Done." -ForegroundColor Green

# Скрипт для создания GitHub репозитория
# Требуется: GitHub Personal Access Token

param(
    [string]$Token = "",
    [string]$RepoName = "telegram-study-bot",
    [string]$Description = "Telegram bot for managing study schedule, homework, and notes"
)

if (-not $Token) {
    Write-Host "Для создания репозитория нужен GitHub Personal Access Token" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Инструкция:" -ForegroundColor Cyan
    Write-Host "1. Перейдите на https://github.com/settings/tokens"
    Write-Host "2. Нажмите 'Generate new token' -> 'Generate new token (classic)'"
    Write-Host "3. Выберите scope: 'repo' (полный доступ к репозиториям)"
    Write-Host "4. Скопируйте токен"
    Write-Host ""
    Write-Host "Затем запустите скрипт с параметром:" -ForegroundColor Green
    Write-Host "  .\create_github_repo.ps1 -Token YOUR_TOKEN"
    exit 1
}

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = $RepoName
    description = $Description
    private = $false
} | ConvertTo-Json

Write-Host "Создание репозитория на GitHub..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "Репозиторий успешно создан!" -ForegroundColor Green
    Write-Host "URL: $($response.html_url)" -ForegroundColor Green
    
    # Добавляем remote и пушим
    Write-Host ""
    Write-Host "Добавление remote и загрузка кода..." -ForegroundColor Cyan
    
    $repoUrl = $response.clone_url
    git remote remove origin 2>$null
    git remote add origin $repoUrl
    git push -u origin main
    
    Write-Host ""
    Write-Host "Готово! Репозиторий создан и код загружен." -ForegroundColor Green
    Write-Host "Просмотреть: $($response.html_url)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Ошибка при создании репозитория:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}


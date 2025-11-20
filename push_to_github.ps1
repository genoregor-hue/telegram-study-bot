# Скрипт для загрузки кода на GitHub
# Используйте после создания репозитория на github.com/new

param(
    [string]$Username = ""
)

if (-not $Username) {
    Write-Host "Введите ваш GitHub username:" -ForegroundColor Yellow
    $Username = Read-Host
}

if (-not $Username) {
    Write-Host "Username не указан. Выход." -ForegroundColor Red
    exit 1
}

$repoUrl = "https://github.com/$Username/telegram-study-bot.git"

Write-Host "Добавление remote origin..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $repoUrl

Write-Host "Загрузка кода на GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Готово! Код загружен на GitHub." -ForegroundColor Green
    Write-Host "Репозиторий: https://github.com/$Username/telegram-study-bot" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Ошибка при загрузке. Проверьте:" -ForegroundColor Red
    Write-Host "1. Репозиторий создан на GitHub" -ForegroundColor Yellow
    Write-Host "2. Правильный username: $Username" -ForegroundColor Yellow
    Write-Host "3. У вас есть права на запись в репозиторий" -ForegroundColor Yellow
}


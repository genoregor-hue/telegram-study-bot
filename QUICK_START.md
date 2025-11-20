# Быстрый старт - создание GitHub репозитория

## Вариант 1: Автоматически (через скрипт)

1. Получите GitHub Personal Access Token:
   - Перейдите на https://github.com/settings/tokens
   - Нажмите "Generate new token" → "Generate new token (classic)"
   - Выберите scope: **repo** (полный доступ)
   - Скопируйте токен

2. Запустите скрипт:
```powershell
.\create_github_repo.ps1 -Token YOUR_TOKEN_HERE
```

Скрипт автоматически:
- Создаст репозиторий `telegram-study-bot` на GitHub
- Добавит remote origin
- Загрузит весь код

## Вариант 2: Вручную (через веб-интерфейс)

1. Создайте репозиторий на GitHub:
   - Перейдите на https://github.com/new
   - Repository name: `telegram-study-bot`
   - Description: `Telegram bot for managing study schedule, homework, and notes`
   - Visibility: **Public**
   - НЕ создавайте README, .gitignore или лицензию
   - Нажмите "Create repository"

2. Выполните команды (GitHub покажет их после создания):
```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-study-bot.git
git push -u origin main
```

Замените `YOUR_USERNAME` на ваш GitHub username.

## Проверка

После загрузки проверьте репозиторий на GitHub - все файлы должны быть там.


# Создание GitHub репозитория

## Самый простой способ

### Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new в браузере
2. Заполните:
   - **Repository name**: `telegram-study-bot`
   - **Description**: `Telegram bot for managing study schedule, homework, and notes`
   - **Visibility**: выберите **Public**
   - **НЕ** ставьте галочки на README, .gitignore, license
3. Нажмите **"Create repository"**

### Шаг 2: Загрузите код

После создания GitHub покажет страницу с инструкциями. Выполните эти команды:

```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-study-bot.git
git branch -M main
git push -u origin main
```

**Замените `YOUR_USERNAME` на ваш GitHub username!**

### Готово!

После выполнения команд ваш код будет загружен на GitHub.

---

## Альтернатива: Автоматический способ

Если хотите автоматизировать, используйте скрипт `create_github_repo.ps1`:

1. Получите GitHub Personal Access Token:
   - https://github.com/settings/tokens
   - Generate new token (classic)
   - Scope: **repo**
   - Скопируйте токен

2. Запустите:
```powershell
.\create_github_repo.ps1 -Token YOUR_TOKEN
```


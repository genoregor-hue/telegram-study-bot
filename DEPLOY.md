# Развертывание на GitHub - Простая инструкция

## Быстрый способ (2 шага)

### 1. Создайте репозиторий на GitHub

Откройте в браузере: **https://github.com/new**

Заполните:
- **Repository name**: `telegram-study-bot`
- **Description**: `Telegram bot for managing study schedule, homework, and notes`
- **Public** (публичный)
- **НЕ** создавайте README, .gitignore, license

Нажмите **"Create repository"**

### 2. Загрузите код

Скопируйте URL вашего репозитория (будет показан на странице после создания) и выполните:

```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-study-bot.git
git push -u origin main
```

**Замените `YOUR_USERNAME` на ваш GitHub username!**

---

## Готово! ✅

Ваш код теперь на GitHub. Можете поделиться ссылкой на репозиторий.

---

## Альтернатива: Автоматический способ

Если хотите автоматизировать, используйте скрипт:

1. Получите токен: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scope: **repo**
   
2. Запустите:
```powershell
.\create_github_repo.ps1 -Token YOUR_TOKEN
```


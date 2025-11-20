# Настройка GitHub репозитория

## Создание репозитория на GitHub

1. Перейдите на [github.com](https://github.com) и войдите в аккаунт
2. Нажмите кнопку "+" в правом верхнем углу → "New repository"
3. Заполните форму:
   - **Repository name**: `telegram-study-bot`
   - **Description**: `Telegram bot for managing study schedule, homework, and notes`
   - **Visibility**: Public
   - НЕ создавайте README, .gitignore или лицензию (они уже есть)
4. Нажмите "Create repository"

## Подключение локального репозитория

После создания репозитория GitHub покажет инструкции. Выполните:

```bash
cd "C:\Users\eddfd\ucheba 2v"
git remote add origin https://github.com/YOUR_USERNAME/telegram-study-bot.git
git push -u origin main
```

Замените `YOUR_USERNAME` на ваш GitHub username.

## Альтернативный способ (через SSH)

Если используете SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/telegram-study-bot.git
git push -u origin main
```

## Проверка

После успешного push проверьте репозиторий на GitHub - все файлы должны быть загружены.


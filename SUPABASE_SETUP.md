# Настройка Supabase для Telegram-бота

## Шаг 1: Создание таблиц

Откройте SQL Editor в вашем проекте Supabase и выполните следующий SQL:

```sql
-- Таблица расписания
create table if not exists schedule (
    id bigint primary key generated always as identity,
    date date,
    subject text,
    time text
);

-- Таблица домашних заданий
create table if not exists homework (
    id bigint primary key generated always as identity,
    subject text,
    hw text,
    deadline date
);

-- Создание индексов для оптимизации запросов
create index if not exists idx_schedule_date on schedule(date);
create index if not exists idx_homework_deadline on homework(deadline);
create index if not exists idx_homework_subject on homework(subject);
```

## Шаг 2: Настройка прав доступа

Убедитесь, что таблицы доступны для чтения и записи через anon key:

```sql
-- Разрешить анонимный доступ (для anon key)
ALTER TABLE schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE homework ENABLE ROW LEVEL SECURITY;

-- Политики для schedule
CREATE POLICY "Allow all operations on schedule" ON schedule
    FOR ALL USING (true) WITH CHECK (true);

-- Политики для homework
CREATE POLICY "Allow all operations on homework" ON homework
    FOR ALL USING (true) WITH CHECK (true);
```

## Шаг 3: Проверка подключения

После настройки проверьте подключение, запустив бота:

```bash
python main.py
```

В логах должно появиться сообщение: "Подключение к Supabase успешно установлено"

## Важные замечания

1. **Безопасность**: В продакшене рекомендуется использовать более строгие политики RLS
2. **Резервное копирование**: Настройте автоматическое резервное копирование в Supabase
3. **Мониторинг**: Используйте Dashboard Supabase для мониторинга запросов


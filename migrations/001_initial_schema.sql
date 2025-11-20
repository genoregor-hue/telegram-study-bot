-- Миграция для создания таблиц schedule и homework в Supabase

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


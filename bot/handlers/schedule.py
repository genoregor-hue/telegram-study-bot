# Обработка расписания
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.schedule_states import ScheduleStates
from bot.keyboards.schedule_kb import (
    get_schedule_menu, get_days_keyboard, get_schedule_items_keyboard, get_edit_schedule_keyboard
)
from bot.keyboards.main_menu import get_main_menu
from bot.database.supabase_db import add_schedule as supabase_add_schedule, get_schedule as supabase_get_schedule
from bot.database.supabase_db import get_db
from datetime import date as date_type, timedelta, datetime
from bot.utils.validators import validate_time, validate_text, validate_room
from bot.utils.formatters import format_schedule_day, get_week_dates, get_day_name
from bot.utils.logger import logger

router = Router()


@router.message(F.text == "📅 Расписание")
async def schedule_menu(message: Message):
    await message.answer(
        "📅 <b>Расписание</b>\n\nВыберите действие:",
        reply_markup=get_schedule_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "schedule_add")
async def schedule_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📅 <b>Добавление предмета</b>\n\nВыберите день недели:",
        reply_markup=get_days_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("day_"))
async def schedule_add_day(callback: CallbackQuery, state: FSMContext):
    day_of_week = int(callback.data.split("_")[1])
    await state.update_data(day_of_week=day_of_week)
    await state.set_state(ScheduleStates.waiting_for_subject)
    
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    await callback.message.edit_text(
        f"📅 <b>Добавление предмета</b>\n\n"
        f"День: <b>{days[day_of_week]}</b>\n\n"
        f"Введите название предмета:",
        parse_mode="HTML"
    )


@router.message(ScheduleStates.waiting_for_subject)
async def schedule_add_subject(message: Message, state: FSMContext):
    is_valid, error = validate_text(message.text, min_length=1, max_length=100)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(subject=message.text)
    await state.set_state(ScheduleStates.waiting_for_time)
    await message.answer(
        "🕐 Введите время начала занятия в формате <b>HH:MM</b>\n(например, 09:30):",
        parse_mode="HTML"
    )


@router.message(ScheduleStates.waiting_for_time)
async def schedule_add_time(message: Message, state: FSMContext):
    is_valid, error = validate_time(message.text)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(time=message.text)
    await state.set_state(ScheduleStates.waiting_for_room)
    await message.answer(
        "🚪 Введите номер кабинета (или отправьте /skip, чтобы пропустить):",
        parse_mode="HTML"
    )


@router.message(ScheduleStates.waiting_for_room)
async def schedule_add_room(message: Message, state: FSMContext):
    room = ""
    if message.text and message.text != "/skip":
        is_valid, error = validate_room(message.text)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nПопробуйте снова:")
            return
        room = message.text
    
    data = await state.get_data()
    try:
        # Преобразуем day_of_week в конкретную дату (берем ближайший день недели)
        today = datetime.now().date()
        days_until = data['day_of_week'] - today.weekday()
        if days_until < 0:
            days_until += 7
        schedule_date = today + timedelta(days=days_until)
        
        await supabase_add_schedule(
            date=schedule_date,
            subject=data['subject'],
            time=data['time']
        )
        
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        await message.answer(
            f"✅ <b>Предмет добавлен!</b>\n\n"
            f"День: {days[data['day_of_week']]}\n"
            f"Дата: {schedule_date.strftime('%d.%m.%Y')}\n"
            f"Предмет: {data['subject']}\n"
            f"Время: {data['time']}\n"
            f"Кабинет: {room if room else 'не указан'}",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при добавлении предмета: {e}")
        await message.answer("❌ Произошла ошибка при добавлении предмета.")
        await state.clear()


@router.callback_query(F.data == "schedule_day")
async def schedule_view_day(callback: CallbackQuery):
    await callback.message.edit_text(
        "📅 <b>Просмотр расписания</b>\n\nВыберите день:",
        reply_markup=get_days_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("day_") and F.message.text.startswith("📅 <b>Просмотр расписания</b>"))
async def schedule_show_day(callback: CallbackQuery):
    day_of_week = int(callback.data.split("_")[1])
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    # Преобразуем day_of_week в дату
    today = datetime.now().date()
    days_until = day_of_week - today.weekday()
    if days_until < 0:
        days_until += 7
    schedule_date = today + timedelta(days=days_until)
    
    schedule_list = await supabase_get_schedule(date=schedule_date)
    
    # Преобразуем для форматирования
    formatted_schedule = []
    for item in schedule_list:
        formatted_schedule.append({
            'subject': item.get('subject', ''),
            'time': item.get('time', ''),
            'room': ''  # В Supabase схеме нет поля room
        })
    
    text = format_schedule_day(formatted_schedule, days[day_of_week])
    
    await callback.message.edit_text(
        text,
        reply_markup=get_schedule_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "schedule_week")
async def schedule_view_week(callback: CallbackQuery):
    week_dates = get_week_dates()
    text = "📅 <b>Расписание на неделю</b>\n\n"
    
    for date_obj, day_name in week_dates:
        date_only = date_obj.date()
        schedule_list = await supabase_get_schedule(date=date_only)
        
        # Преобразуем для форматирования
        formatted_schedule = []
        for item in schedule_list:
            formatted_schedule.append({
                'subject': item.get('subject', ''),
                'time': item.get('time', ''),
                'room': ''
            })
        
        text += format_schedule_day(formatted_schedule, day_name) + "\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_schedule_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "schedule_delete")
async def schedule_delete_start(callback: CallbackQuery):
    schedule_list = await supabase_get_schedule()
    if not schedule_list:
        await callback.answer("Нет предметов для удаления", show_alert=True)
        return
    
    # Преобразуем для клавиатуры
    formatted_schedule = []
    for item in schedule_list:
        formatted_schedule.append({
            'id': item.get('id'),
            'subject': item.get('subject', ''),
            'time': item.get('time', ''),
            'room': ''
        })
    
    await callback.message.edit_text(
        "🗑️ <b>Удаление предмета</b>\n\nВыберите предмет для удаления:",
        reply_markup=get_schedule_items_keyboard(formatted_schedule, "delete"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("delete_schedule_"))
async def schedule_delete_confirm(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[-1])
    db = get_db()
    success = await db.delete_schedule(item_id)
    
    if success:
        await callback.answer("✅ Предмет удален", show_alert=True)
        await callback.message.edit_text(
            "✅ Предмет успешно удален!",
            reply_markup=get_schedule_menu()
        )
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "schedule_edit")
async def schedule_edit_start(callback: CallbackQuery):
    schedule_list = await supabase_get_schedule()
    if not schedule_list:
        await callback.answer("Нет предметов для редактирования", show_alert=True)
        return
    
    # Преобразуем для клавиатуры
    formatted_schedule = []
    for item in schedule_list:
        formatted_schedule.append({
            'id': item.get('id'),
            'subject': item.get('subject', ''),
            'time': item.get('time', ''),
            'room': ''
        })
    
    await callback.message.edit_text(
        "✏️ <b>Редактирование расписания</b>\n\nВыберите предмет:",
        reply_markup=get_schedule_items_keyboard(formatted_schedule, "edit"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("edit_schedule_"))
async def schedule_edit_item(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    if len(parts) == 4:  # edit_schedule_subject_123
        field = parts[2]
        item_id = int(parts[3])
        await state.update_data(edit_item_id=item_id, edit_field=field)
        await state.set_state(ScheduleStates.waiting_for_edit_value)
        
        field_names = {
            "subject": "название предмета",
            "time": "время (HH:MM)",
            "room": "номер кабинета"
        }
        
        await callback.message.edit_text(
            f"✏️ Введите новое {field_names.get(field, field)}:",
            parse_mode="HTML"
        )
    else:  # edit_schedule_123
        item_id = int(parts[2])
        await callback.message.edit_text(
            "✏️ <b>Редактирование</b>\n\nЧто вы хотите изменить?",
            reply_markup=get_edit_schedule_keyboard(item_id),
            parse_mode="HTML"
        )


@router.message(ScheduleStates.waiting_for_edit_value)
async def schedule_edit_save(message: Message, state: FSMContext):
    data = await state.get_data()
    item_id = data['edit_item_id']
    field = data['edit_field']
    db = get_db()
    
    try:
        if field == "subject":
            is_valid, error = validate_text(message.text, min_length=1, max_length=100)
            if not is_valid:
                await message.answer(f"❌ {error}\n\nПопробуйте снова:")
                return
            success = await db.update_schedule(item_id, subject=message.text)
        elif field == "time":
            is_valid, error = validate_time(message.text)
            if not is_valid:
                await message.answer(f"❌ {error}\n\nПопробуйте снова:")
                return
            success = await db.update_schedule(item_id, time=message.text)
        elif field == "room":
            # В Supabase схеме нет поля room, пропускаем
            await message.answer("⚠️ Поле 'кабинет' не поддерживается в текущей схеме базы данных.")
            await state.clear()
            return
        else:
            success = False
        
        if success:
            await message.answer(
                "✅ Изменения сохранены!",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer("❌ Ошибка при сохранении изменений.")
        
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при редактировании: {e}")
        await message.answer("❌ Произошла ошибка.")
        await state.clear()


@router.callback_query(F.data == "schedule_back")
async def schedule_back(callback: CallbackQuery):
    await schedule_menu(callback.message)
    await callback.answer()


"""
Обработчики для работы с домашними заданиями
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from bot.states.homework_states import HomeworkStates
from bot.keyboards.homework_kb import (
    get_homework_menu, get_homework_items_keyboard, get_edit_homework_keyboard
)
from bot.keyboards.main_menu import get_main_menu
from bot.database.supabase_db import add_homework as supabase_add_homework, get_homework as supabase_get_homework
from bot.database.supabase_db import get_db
from datetime import date as date_type
from bot.utils.validators import validate_text, validate_date
from bot.utils.formatters import format_homework_list, format_date, get_week_dates
from bot.utils.logger import logger
from bot.database.achievements_model import check_achievements

router = Router()


@router.message(F.text == "📘 Домашние задания")
async def homework_menu(message: Message):
    """Меню домашних заданий"""
    await message.answer(
        "📘 <b>Домашние задания</b>\n\nВыберите действие:",
        reply_markup=get_homework_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "homework_add")
async def homework_add_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления ДЗ"""
    await state.set_state(HomeworkStates.waiting_for_subject)
    await callback.message.edit_text(
        "📘 <b>Добавление домашнего задания</b>\n\nВведите название предмета:",
        parse_mode="HTML"
    )


@router.message(HomeworkStates.waiting_for_subject)
async def homework_add_subject(message: Message, state: FSMContext):
    """Ввод предмета"""
    is_valid, error = validate_text(message.text, min_length=1, max_length=100)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(subject=message.text)
    await state.set_state(HomeworkStates.waiting_for_task)
    await message.answer("📝 Введите описание задания:")


@router.message(HomeworkStates.waiting_for_task)
async def homework_add_task(message: Message, state: FSMContext):
    """Ввод задания"""
    is_valid, error = validate_text(message.text, min_length=1, max_length=500)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(task=message.text)
    await state.set_state(HomeworkStates.waiting_for_deadline)
    await message.answer(
        "📅 Введите дедлайн в формате <b>DD.MM.YY</b> или <b>DD.MM.YYYY</b>\n"
        "(или отправьте /skip, чтобы пропустить):",
        parse_mode="HTML"
    )


@router.message(HomeworkStates.waiting_for_deadline)
async def homework_add_deadline(message: Message, state: FSMContext):
    """Ввод дедлайна"""
    deadline = None
    if message.text and message.text != "/skip":
        is_valid, error, date_obj = validate_date(message.text)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nПопробуйте снова:")
            return
        deadline = date_obj
    
    data = await state.get_data()
    try:
        deadline_date = deadline.date() if deadline else None
        await supabase_add_homework(
            subject=data['subject'],
            text=data['task'],
            deadline=deadline_date
        )
        
        deadline_text = format_date(deadline) if deadline else "не указан"
        await message.answer(
            f"✅ <b>Домашнее задание добавлено!</b>\n\n"
            f"Предмет: {data['subject']}\n"
            f"Задание: {data['task']}\n"
            f"Дедлайн: {deadline_text}",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при добавлении ДЗ: {e}")
        await message.answer("❌ Произошла ошибка при добавлении ДЗ.")
        await state.clear()


@router.callback_query(F.data == "homework_today")
async def homework_view_today(callback: CallbackQuery):
    """Просмотр ДЗ на сегодня"""
    today = datetime.now().date()
    homework_list = await supabase_get_homework(deadline=today)
    
    # Преобразуем данные для форматирования
    formatted_homework = []
    for item in homework_list:
        formatted_homework.append({
            'subject': item.get('subject', ''),
            'task': item.get('hw', ''),
            'deadline': item.get('deadline', ''),
            'is_completed': False  # Supabase схема не имеет этого поля
        })
    
    text = format_homework_list(formatted_homework, "Домашние задания на сегодня")
    
    await callback.message.edit_text(
        text,
        reply_markup=get_homework_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "homework_week")
async def homework_view_week(callback: CallbackQuery):
    """Просмотр ДЗ на неделю"""
    week_dates = get_week_dates()
    text = "📘 <b>Домашние задания на неделю</b>\n\n"
    
    for date_obj, day_name in week_dates:
        date_only = date_obj.date()
        homework_list = await supabase_get_homework(deadline=date_only)
        if homework_list:
            text += f"📅 <b>{day_name}</b>\n"
            for item in homework_list:
                subject = item.get('subject', '')
                task = item.get('hw', '')
                deadline = item.get('deadline', '')
                
                text += f"⏳ {subject}: {task}\n"
                if deadline:
                    if isinstance(deadline, str):
                        deadline_date = datetime.fromisoformat(deadline).date()
                    else:
                        deadline_date = deadline
                    text += f"   📅 До: {format_date(datetime.combine(deadline_date, datetime.min.time()))}\n"
            text += "\n"
    
    if text == "📘 <b>Домашние задания на неделю</b>\n\n":
        text += "Нет заданий на эту неделю"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_homework_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "homework_by_subject")
async def homework_by_subject_start(callback: CallbackQuery, state: FSMContext):
    """Начало поиска по предмету"""
    await state.set_state(HomeworkStates.waiting_for_subject)
    await callback.message.edit_text(
        "🔍 Введите название предмета:",
        parse_mode="HTML"
    )


@router.message(HomeworkStates.waiting_for_subject, F.text != "📘 Домашние задания")
async def homework_show_by_subject(message: Message, state: FSMContext):
    """Показ ДЗ по предмету"""
    subject = message.text
    homework_list = await supabase_get_homework(subject=subject)
    
    # Преобразуем данные для форматирования
    formatted_homework = []
    for item in homework_list:
        formatted_homework.append({
            'subject': item.get('subject', ''),
            'task': item.get('hw', ''),
            'deadline': item.get('deadline', ''),
            'is_completed': False
        })
    
    text = format_homework_list(formatted_homework, f"Домашние задания: {subject}")
    
    await message.answer(
        text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data == "homework_complete")
async def homework_complete_start(callback: CallbackQuery):
    """Начало отметки выполнения"""
    homework_list = await supabase_get_homework()
    if not homework_list:
        await callback.answer("Нет заданий", show_alert=True)
        return
    
    # Преобразуем для клавиатуры
    formatted_homework = []
    for item in homework_list:
        formatted_homework.append({
            'id': item.get('id'),
            'subject': item.get('subject', ''),
            'task': item.get('hw', ''),
            'is_completed': False
        })
    
    await callback.message.edit_text(
        "✅ <b>Отметить как выполненное</b>\n\nВыберите задание:",
        reply_markup=get_homework_items_keyboard(formatted_homework, "complete"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("complete_homework_"))
async def homework_complete_confirm(callback: CallbackQuery):
    """Подтверждение выполнения"""
    # В Supabase схеме нет поля is_completed, поэтому просто удаляем задание
    item_id = int(callback.data.split("_")[-1])
    db = get_db()
    success = await db.delete_homework(item_id)
    
    if success:
        # Проверка достижений
        try:
            bot = callback.bot
            await check_achievements(callback.from_user.id, bot)
        except Exception as e:
            logger.error(f"Ошибка при проверке достижений: {e}")
        
        await callback.answer("✅ Задание отмечено как выполненное и удалено", show_alert=True)
        await callback.message.edit_text(
            "✅ Задание успешно отмечено как выполненное!",
            reply_markup=get_homework_menu()
        )
    else:
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "homework_delete")
async def homework_delete_start(callback: CallbackQuery):
    """Начало удаления"""
    homework_list = await supabase_get_homework()
    if not homework_list:
        await callback.answer("Нет заданий для удаления", show_alert=True)
        return
    
    # Преобразуем для клавиатуры
    formatted_homework = []
    for item in homework_list:
        formatted_homework.append({
            'id': item.get('id'),
            'subject': item.get('subject', ''),
            'task': item.get('hw', ''),
            'is_completed': False
        })
    
    await callback.message.edit_text(
        "🗑️ <b>Удаление задания</b>\n\nВыберите задание:",
        reply_markup=get_homework_items_keyboard(formatted_homework, "delete"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("delete_homework_"))
async def homework_delete_confirm(callback: CallbackQuery):
    """Подтверждение удаления"""
    item_id = int(callback.data.split("_")[-1])
    db = get_db()
    success = await db.delete_homework(item_id)
    
    if success:
        await callback.answer("✅ Задание удалено", show_alert=True)
        await callback.message.edit_text(
            "✅ Задание успешно удалено!",
            reply_markup=get_homework_menu()
        )
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "homework_edit")
async def homework_edit_start(callback: CallbackQuery):
    """Начало редактирования"""
    homework_list = await supabase_get_homework()
    if not homework_list:
        await callback.answer("Нет заданий для редактирования", show_alert=True)
        return
    
    # Преобразуем для клавиатуры
    formatted_homework = []
    for item in homework_list:
        formatted_homework.append({
            'id': item.get('id'),
            'subject': item.get('subject', ''),
            'task': item.get('hw', ''),
            'is_completed': False
        })
    
    await callback.message.edit_text(
        "✏️ <b>Редактирование задания</b>\n\nВыберите задание:",
        reply_markup=get_homework_items_keyboard(formatted_homework, "edit"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("edit_homework_"))
async def homework_edit_item(callback: CallbackQuery, state: FSMContext):
    """Редактирование задания"""
    parts = callback.data.split("_")
    if len(parts) == 4:  # edit_homework_subject_123
        field = parts[2]
        item_id = int(parts[3])
        await state.update_data(edit_item_id=item_id, edit_field=field)
        await state.set_state(HomeworkStates.waiting_for_edit_value)
        
        field_names = {
            "subject": "название предмета",
            "task": "описание задания",
            "deadline": "дедлайн (DD.MM.YY)"
        }
        
        await callback.message.edit_text(
            f"✏️ Введите новое {field_names.get(field, field)}:",
            parse_mode="HTML"
        )
    else:  # edit_homework_123
        item_id = int(parts[2])
        await callback.message.edit_text(
            "✏️ <b>Редактирование</b>\n\nЧто вы хотите изменить?",
            reply_markup=get_edit_homework_keyboard(item_id),
            parse_mode="HTML"
        )


@router.message(HomeworkStates.waiting_for_edit_value)
async def homework_edit_save(message: Message, state: FSMContext):
    """Сохранение изменений"""
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
            success = await db.update_homework(item_id, subject=message.text)
        elif field == "task":
            is_valid, error = validate_text(message.text, min_length=1, max_length=500)
            if not is_valid:
                await message.answer(f"❌ {error}\n\nПопробуйте снова:")
                return
            success = await db.update_homework(item_id, hw=message.text)
        elif field == "deadline":
            if message.text == "/skip":
                success = await db.update_homework(item_id, deadline=None)
            else:
                is_valid, error, date_obj = validate_date(message.text)
                if not is_valid:
                    await message.answer(f"❌ {error}\n\nПопробуйте снова:")
                    return
                success = await db.update_homework(item_id, deadline=date_obj.date())
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
        logger.error(f"Ошибка при редактировании ДЗ: {e}")
        await message.answer("❌ Произошла ошибка.")
        await state.clear()


@router.callback_query(F.data == "homework_back")
async def homework_back(callback: CallbackQuery):
    """Возврат в меню ДЗ"""
    await homework_menu(callback.message)
    await callback.answer()


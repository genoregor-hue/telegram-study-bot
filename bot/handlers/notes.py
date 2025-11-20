"""
Обработчики для работы с заметками
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.notes_states import NotesStates
from bot.keyboards.notes_kb import (
    get_notes_menu, get_notes_list_keyboard, get_note_actions_keyboard
)
from bot.keyboards.main_menu import get_main_menu
from bot.database.notes_model import (
    add_note, get_all_notes, get_note, search_notes,
    update_note, delete_note
)
from bot.utils.validators import validate_text
from bot.utils.formatters import format_notes_list, format_date
from bot.utils.logger import logger

router = Router()


@router.message(F.text == "📝 Заметки")
async def notes_menu(message: Message):
    """Меню заметок"""
    await message.answer(
        "📝 <b>Заметки</b>\n\nВыберите действие:",
        reply_markup=get_notes_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "notes_add")
async def notes_add_start(callback: CallbackQuery, state: FSMContext):
    """Начало создания заметки"""
    await state.set_state(NotesStates.waiting_for_title)
    await callback.message.edit_text(
        "📝 <b>Создание заметки</b>\n\nВведите заголовок заметки:",
        parse_mode="HTML"
    )


@router.message(NotesStates.waiting_for_title)
async def notes_add_title(message: Message, state: FSMContext):
    """Ввод заголовка"""
    is_valid, error = validate_text(message.text, min_length=1, max_length=100)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    await state.update_data(title=message.text)
    await state.set_state(NotesStates.waiting_for_content)
    await message.answer("📄 Введите содержание заметки (или отправьте /skip, чтобы пропустить):")


@router.message(NotesStates.waiting_for_content)
async def notes_add_content(message: Message, state: FSMContext):
    """Ввод содержания"""
    content = ""
    if message.text and message.text != "/skip":
        is_valid, error = validate_text(message.text, min_length=1, max_length=1000)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nПопробуйте снова:")
            return
        content = message.text
    
    data = await state.get_data()
    try:
        await add_note(
            user_id=message.from_user.id,
            title=data['title'],
            content=content
        )
        
        await message.answer(
            f"✅ <b>Заметка создана!</b>\n\n"
            f"Заголовок: {data['title']}\n"
            f"Содержание: {content if content else 'не указано'}",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при создании заметки: {e}")
        await message.answer("❌ Произошла ошибка при создании заметки.")
        await state.clear()


@router.callback_query(F.data == "notes_all")
async def notes_view_all(callback: CallbackQuery):
    """Просмотр всех заметок"""
    notes = await get_all_notes(callback.from_user.id)
    if not notes:
        await callback.message.edit_text(
            "📝 <b>Заметки</b>\n\nНет заметок",
            reply_markup=get_notes_menu(),
            parse_mode="HTML"
        )
        return
    
    text = format_notes_list(notes)
    await callback.message.edit_text(
        text,
        reply_markup=get_notes_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "notes_search")
async def notes_search_start(callback: CallbackQuery, state: FSMContext):
    """Начало поиска"""
    await state.set_state(NotesStates.waiting_for_search)
    await callback.message.edit_text(
        "🔍 <b>Поиск заметок</b>\n\nВведите поисковый запрос:",
        parse_mode="HTML"
    )


@router.message(NotesStates.waiting_for_search)
async def notes_search_execute(message: Message, state: FSMContext):
    """Выполнение поиска"""
    query = message.text
    notes = await search_notes(message.from_user.id, query)
    
    if not notes:
        await message.answer(
            f"🔍 <b>Результаты поиска</b>\n\nПо запросу '{query}' ничего не найдено.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        text = f"🔍 <b>Результаты поиска: '{query}'</b>\n\n"
        for idx, note in enumerate(notes, 1):
            title = note.get('title', 'Без названия')
            content = note.get('content', '')
            preview = content[:50] + "..." if len(content) > 50 else content
            text += f"<b>{idx}.</b> {title}\n{preview}\n\n"
        
        await message.answer(
            text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    
    await state.clear()


@router.callback_query(F.data == "notes_edit")
async def notes_edit_start(callback: CallbackQuery):
    """Начало редактирования"""
    notes = await get_all_notes(callback.from_user.id)
    if not notes:
        await callback.answer("Нет заметок для редактирования", show_alert=True)
        return
    
    await callback.message.edit_text(
        "✏️ <b>Редактирование заметки</b>\n\nВыберите заметку:",
        reply_markup=get_notes_list_keyboard(notes, "edit"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("edit_note_"))
async def notes_edit_item(callback: CallbackQuery, state: FSMContext):
    """Редактирование заметки"""
    note_id = int(callback.data.split("_")[-1])
    note = await get_note(callback.from_user.id, note_id)
    
    if not note:
        await callback.answer("Заметка не найдена", show_alert=True)
        return
    
    await state.update_data(edit_note_id=note_id)
    await state.set_state(NotesStates.editing_title)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование заметки</b>\n\n"
        f"Текущий заголовок: {note.get('title', '')}\n\n"
        f"Введите новый заголовок (или отправьте /skip, чтобы оставить прежний):",
        parse_mode="HTML"
    )


@router.message(NotesStates.editing_title)
async def notes_edit_title(message: Message, state: FSMContext):
    """Редактирование заголовка"""
    data = await state.get_data()
    note_id = data.get('edit_note_id')
    
    if not note_id:
        await state.clear()
        return
    
    title = None
    if message.text and message.text != "/skip":
        is_valid, error = validate_text(message.text, min_length=1, max_length=100)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nПопробуйте снова:")
            return
        title = message.text
        await state.update_data(new_title=title)
    
    await state.set_state(NotesStates.editing_content)
    await message.answer("📄 Введите новое содержание (или отправьте /skip, чтобы оставить прежнее):")


@router.message(NotesStates.editing_content)
async def notes_edit_content(message: Message, state: FSMContext):
    """Редактирование содержания"""
    data = await state.get_data()
    note_id = data.get('edit_note_id')
    
    if not note_id:
        await state.clear()
        return
    
    content = None
    if message.text and message.text != "/skip":
        is_valid, error = validate_text(message.text, min_length=1, max_length=1000)
        if not is_valid:
            await message.answer(f"❌ {error}\n\nПопробуйте снова:")
            return
        content = message.text
    
    try:
        # Получаем текущие данные заметки
        note = await get_note(message.from_user.id, note_id)
        if not note:
            await message.answer("❌ Заметка не найдена.")
            await state.clear()
            return
        
        title = data.get('new_title') or note.get('title')
        if content is None:
            content = note.get('content', '')
        
        success = await update_note(
            message.from_user.id,
            note_id,
            title=title,
            content=content
        )
        
        if success:
            await message.answer(
                "✅ Заметка успешно обновлена!",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer("❌ Ошибка при обновлении заметки.")
        
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при редактировании заметки: {e}")
        await message.answer("❌ Произошла ошибка.")
        await state.clear()


@router.callback_query(F.data == "notes_delete")
async def notes_delete_start(callback: CallbackQuery):
    """Начало удаления"""
    notes = await get_all_notes(callback.from_user.id)
    if not notes:
        await callback.answer("Нет заметок для удаления", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🗑️ <b>Удаление заметки</b>\n\nВыберите заметку:",
        reply_markup=get_notes_list_keyboard(notes, "delete"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("delete_note_"))
async def notes_delete_confirm(callback: CallbackQuery):
    """Подтверждение удаления"""
    note_id = int(callback.data.split("_")[-1])
    success = await delete_note(callback.from_user.id, note_id)
    
    if success:
        await callback.answer("✅ Заметка удалена", show_alert=True)
        await callback.message.edit_text(
            "✅ Заметка успешно удалена!",
            reply_markup=get_notes_menu()
        )
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "notes_back")
async def notes_back(callback: CallbackQuery):
    """Возврат в меню заметок"""
    await notes_menu(callback.message)
    await callback.answer()


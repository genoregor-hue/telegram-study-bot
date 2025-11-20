# Глобальная обработка ошибок
from aiogram import Router
from aiogram.types import ErrorEvent, Update
from bot.utils.logger import logger

router = Router()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Ошибка: {event.exception}", exc_info=event.exception)
    
    # Пытаемся отправить сообщение пользователю, если это возможно
    try:
        update: Update = event.update
        if update.message:
            await update.message.answer(
                "❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "❌ Произошла ошибка. Попробуйте позже.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке ошибки: {e}")


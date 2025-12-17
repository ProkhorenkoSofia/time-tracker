import os
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Конфигурация
API_URL = os.environ.get('API_URL', 'https://time-tracker-z6co.onrender.com/api/v1')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем/регистрируем пользователя в системе
    response = requests.post(f'{API_URL}/telegram/auth', json={
        'telegram_id': str(user.id),
        'username': user.username or user.first_name
    })
    
    if response.status_code == 200:
        data = response.json()
        
        if data['status'] == 'authenticated':
            keyboard = [
                [InlineKeyboardButton("➕ Добавить событие", callback_data='add_event')],
                [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
                [InlineKeyboardButton("🏷️ Мои категории", callback_data='categories')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f'Привет, {user.first_name}! 👋\n'
                f'Вы авторизованы как {data["username"]}\n'
                'Выберите действие:',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                'Для использования бота необходимо сначала зарегистрироваться '
                'через веб-интерфейс:\n'
                f'{data["registration_url"]}'
            )
    else:
        await update.message.reply_text('Ошибка подключения к серверу. Попробуйте позже.')

async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление события через бота"""
    query = update.callback_query
    await query.answer()
    
    # Получаем категории пользователя
    user_id = query.from_user.id
    response = requests.get(
        f'{API_URL}/telegram/categories',
        headers={'X-Telegram-ID': str(user_id)}
    )
    
    if response.status_code == 200:
        categories = response.json()['quick_replies']
        
        keyboard = []
        row = []
        for i, cat in enumerate(categories):
            row.append(InlineKeyboardButton(cat['text'], callback_data=cat['callback_data']))
            if (i + 1) % 2 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            'Выберите категорию:',
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text('Сначала создайте категории через веб-интерфейс.')

async def quick_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрое добавление события по коду"""
    message_text = update.message.text.strip().upper()
    user_id = update.effective_user.id
    
    # Пытаемся создать событие по коду
    response = requests.post(
        f'{API_URL}/telegram/quick',
        headers={'X-Telegram-ID': str(user_id)},
        json={'code': message_text, 'duration': 60}
    )
    
    if response.status_code == 201:
        data = response.json()
        await update.message.reply_text(f'✅ Добавлено: {data["category"]} (60 мин)')
    else:
        await update.message.reply_text('Категория не найдена. Используйте /start для выбора.')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение статистики"""
    user_id = update.effective_user.id
    
    response = requests.get(
        f'{API_URL}/telegram/stats',
        headers={'X-Telegram-ID': str(user_id)}
    )
    
    if response.status_code == 200:
        stats = response.json()
        message = (
            f'📊 Ваша статистика:\n'
            f'• Событий сегодня: {stats["today"]}\n'
            f'• Всего событий: {stats["total"]}\n'
            f'• План: {stats["plan"]} | Факт: {stats["fact"]}'
        )
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Не удалось получить статистику.')

def main():
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(add_event, pattern='^add_event$'))
    application.add_handler(CallbackQueryHandler(add_event, pattern='^cat_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quick_event))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

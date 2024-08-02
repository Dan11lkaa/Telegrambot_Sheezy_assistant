from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import BotCommand

klav = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изучить тему📚'), KeyboardButton(text='Предложить идею💡')],
    [KeyboardButton(text='Решить задачу🤔'), KeyboardButton(text='Ответить на вопрос❓')],
    [KeyboardButton(text='Очистить память🧠')]
])

commands = [BotCommand(command='start', description='начать/показать описание функционала'),
            BotCommand(command='help', description='покзать шаблон подачи команд к планировщику с примерами'),
            BotCommand(command='add', description='добавить новую задачу'),
            BotCommand(command='view', description='показать задачи для конкретного пользователя'),
            BotCommand(command='view_all', description='показать все задачи'),
            BotCommand(command='update', description='обновить существующею задачу'),
            BotCommand(command='list_users', description='показать список ID пользователей'),
            BotCommand(command='delete', description='удалить задачу'),
            BotCommand(command='delete_user', description='удалить пользователя'),
            BotCommand(command='delete_all_tasks', description='удалить все задачи'),
            BotCommand(command='delete_all_users', description='удалить всех пользователей и задачи')
]

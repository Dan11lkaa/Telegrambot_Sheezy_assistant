from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from gigachat import GigaChat
from app.states import AI
from config import AI_TOKEN
from gigachat.models import Chat, Messages, MessagesRole
from app.keyboard import klav
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, Task, async_session
import datetime as dt
import pytz


router = Router()
last_start_time = dt.datetime.now(pytz.utc)
user_last_message_time = {}
query_count = 0
dictionary = {'Изучить тему📚': 'предоставь информацию по такой теме максимально понятно:',
              'Предложить идею💡': 'предложи по такому запросу максимально реалистичную идею:',
              'Решить задачу🤔': 'реши макисмально правильно и правдаподобно данную задачу:',
              'Ответить на вопрос❓': 'ответь максимально понятно и правильно на следующий вопрос:'}
key = ''
def is_message_old(message: Message) -> bool:
    message_time = message.date.replace(tzinfo=pytz.utc)
    return message_time < last_start_time

def is_spam(message: Message) -> bool:
    user_id = message.from_user.id
    current_time = dt.datetime.now(pytz.utc)
    last_message_time = user_last_message_time.get(user_id)
    if last_message_time is None:
        user_last_message_time[user_id] = current_time
        return False
    if (current_time - last_message_time).total_seconds() < 5:
        return True
    user_last_message_time[user_id] = current_time
    return False

chatik = Chat(
        messages=[Messages(role=MessagesRole.SYSTEM,
                           content='Ты в роли кота-ассистента по имени Шизи, который помогает пользователям '
                                   'или команде пользователей решать их задачи, которые они тебе пишут в запросе')])

async def get_user(session: AsyncSession, user_name: str):
    result = await session.execute(select(User).filter_by(name=user_name))
    return result.scalars().first()

async def get_tasks(session: AsyncSession, user_id: int):
    result = await session.execute(select(Task).filter_by(user_id=user_id))
    return result.scalars().all()

async def get_all_tasks(session: AsyncSession):
    result = await session.execute(select(Task))
    return result.scalars().all()

async def get_all_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()

@router.message(CommandStart())
async def cmd_start(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    text = 'Меня разработал: <a href="https://t.me/Mandan27">Mandan27</a>'
    await message.answer('Привет, я Шизи - твой пушистый помошник для твоих задач!🐱')

    await message.answer('Кратко о функционале:\n⬅️ Слева меню для работы с планировщиком задач, основанный на базе данных "SQLAlchemy"💿'
                         '(в группе введи слэш "/")\n➡️'
                         ' Справа клавиатура для вазимодействия со мной(также можешь писать другие действия при необходимости)🐾\n'
                         'Жду твоего запроса!✏️')
    await message.answer('Также не забывай честенько очищать память, нажав на клавиауре кпопку \"Очистить память🧠\".'
                         ' Так ты будешь экономить токены автора и улучшать качество диалога.'
                         ' Если у меня будет больше 10 запросов в памяти к моему ИИ я буду тебе об этом напоминать каждый запрос!🧶')
    await message.answer(text, parse_mode='HTML', reply_markup=klav)

@router.message(Command('add'))
async def cmd_add(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        parts = message.text.split(', ')
        user_name = parts[0].replace('/add ', '')
        description = parts[1]
        task_date = datetime.strptime(parts[2], '%d.%m.%Y').date()

        async with async_session() as session:
            user = await get_user(session, user_name)
            if not user:
                user = User(name=user_name)
                session.add(user)
                await session.commit()

            task = Task(description=description, date=task_date, user_id=user.id)
            session.add(task)
            await session.commit()
            await message.reply(f"Задача добавлена: {description} на {task_date}", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при добавлении задачи: {e}", reply_markup=klav)


@router.message(Command('view'))
async def cmd_view(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    user_name = message.text.replace('/view ', '')
    async with async_session() as session:
        user = await get_user(session, user_name)
        if not user:
            await message.reply("Пользователь не найден.", reply_markup=klav)
            return

        tasks = await get_tasks(session, user.id)
        if not tasks:
            await message.reply("Задачи не найдены.", reply_markup=klav)
            return

        task_list = '\n'.join([f"{task.description} на {task.date}" for task in tasks])
        await message.reply(f"Задачи для {user_name}:\n{task_list}", reply_markup=klav)


@router.message(Command('view_all'))
async def cmd_view_all(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    async with async_session() as session:
        tasks = await get_all_tasks(session)
        if not tasks:
            await message.reply("Нет задач в системе.", reply_markup=klav)
            return

        task_list = '\n'.join([f"ID: {task.id}, Описание: {task.description}, Дата: {task.date}" for task in tasks])
        await message.reply(f"Все задачи:\n{task_list}", reply_markup=klav)


@router.message(Command('update'))
async def cmd_update(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        parts = message.text.split(', ')
        task_id = int(parts[0].replace('/update ', ''))
        description = parts[1]
        task_date = datetime.strptime(parts[2], '%d.%m.%Y').date()

        async with async_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                await message.reply("Задача не найдена.", reply_markup=klav)
                return

            task.description = description
            task.date = task_date
            await session.commit()
            await message.reply(f"Задача обновлена: {description} на {task_date}", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при обновлении задачи: {e}", reply_markup=klav)


@router.message(Command('delete'))
async def cmd_delete(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        task_id = int(message.text.replace('/delete ', ''))

        async with async_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                await message.reply("Задача не найдена.", reply_markup=klav)
                return

            await session.delete(task)
            await session.commit()
            await message.reply("Задача удалена.", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при удалении задачи: {e}", reply_markup=klav)


@router.message(Command('list_users'))
async def cmd_list_users(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    async with async_session() as session:
        users = await get_all_users(session)
        if not users:
            await message.reply("Нет пользователей в системе.", reply_markup=klav)
            return

        user_list = '\n'.join([f"ID: {user.id}, Имя: {user.name}" for user in users])
        await message.reply(f"Все пользователи:\n{user_list}", reply_markup=klav)

@router.message(Command('delete_user'))
async def cmd_delete_user(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        user_id = int(message.text.replace('/delete_user ', ''))

        async with async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                await message.reply("Пользователь не найден.", reply_markup=klav)
                return

            tasks = await get_tasks(session, user_id)
            for task in tasks:
                await session.delete(task)

            await session.delete(user)
            await session.commit()
            await message.reply(f"Пользователь с ID {user_id} удалён.", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при удалении пользователя: {e}", reply_markup=klav)

@router.message(Command('delete_all_tasks'))
async def cmd_delete_all_tasks(message:Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        async with async_session() as session:
            tasks = await get_all_tasks(session)
            for task in tasks:
                await session.delete(task)
            await session.commit()
            await message.reply("Все задачи удалены.", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при удалении задач: {e}", reply_markup=klav)

@router.message(Command('delete_all_users'))
async def cmd_delete_all_users(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    try:
        async with async_session() as session:
            users = await get_all_users(session)
            for user in users:
                tasks = await get_tasks(session, user.id)
                for task in tasks:
                    await session.delete(task)
                await session.delete(user)
            await session.commit()
            await message.reply("Все пользователи и их задачи удалены.", reply_markup=klav)
    except Exception as e:
        await message.reply(f"Ошибка при удалении пользователей: {e}", reply_markup=klav)

@router.message(Command('help'))
async def cmd_help(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    help_text = (
        "Команды для взаимодействия с базой данных:\n\n"
        "add [Имя пользователя], [Описание задачи], [Дата]\n"
        "Пример: add Иван, вытереть пол, 16.12.2024\n\n"
        "view [Имя пользователя]\n"
        "Пример: view Иван\n\n"
        "view_all\n"
        "Пример: view_all\n\n"
        "update [ID задачи], [Новое описание задачи], [Новая дата]\n"
        "Пример: update 1, вымыть окна, 20.12.2024\n\n"
        "delete [ID задачи]\n"
        "Пример: delete 1\n\n"
        "list_users\n"
        "Пример: list_users\n\n"
        "delete_user [ID пользователя]\n"
        "Пример: delete_user 1\n\n"
        "delete_all_tasks\n"
        "Пример: delete_all_tasks\n\n"
        "delete_all_users\n"
        "Пример: delete_all_users\n"
    )
    await message.reply(help_text, reply_markup=klav)


@router.message(F.text == 'Изучить тему📚')
async def word_1(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
    global key
    key = message.text
    await message.answer(f'вы выбрали действие: {key}', reply_markup=klav)

@router.message(F.text == 'Предложить идею💡')
async def word_1(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
    global key
    key = message.text
    await message.answer(f'вы выбрали действие: {key}', reply_markup=klav)

@router.message(F.text == 'Решить задачу🤔')
async def word_1(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
    global key
    key = message.text
    await message.answer(f'вы выбрали действие: {key}', reply_markup=klav)

@router.message(F.text == 'Ответить на вопрос❓')
async def word_1(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
    global key
    key = message.text
    await message.answer(f'вы выбрали действие: {key}', reply_markup=klav)

@router.message(F.text == 'Очистить память🧠')
async def clear(message: Message):
    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    chatik.messages = [Messages(role=MessagesRole.SYSTEM,
                               content='Ты в роли кота-ассистента по имени Шизи, который помогает пользователям '
                                       'или команде пользователей решать их задачи, которые они тебе пишут в запросе')]
    global query_count
    query_count = 0
    await message.answer('Память очищена!', reply_markup=klav)

@router.message(AI.answer)
async def answer(message: Message):
    await message.answer('Подожди, ещё не ответил на предыдущий вопрос!⌛', reply_markup=klav)

@router.message(F.text)
async def gigachatka(message: Message, state: FSMContext):

    if is_message_old(message):
        return
    if is_spam(message):
        await message.answer('Пожалуйста, не спамьте! Подождите 5 секунд перед отправкой следующего сообщения.', reply_markup=klav)
        return
    await state.set_state(AI.answer)
    with GigaChat(credentials=AI_TOKEN, verify_ssl_certs=False) as giga:
        global dictionary, key, query_count
        if key:
            chatik.messages.append(Messages(role=MessagesRole.USER, content=f'{dictionary[key]} {message.text}'))
        else:
            chatik.messages.append(Messages(role=MessagesRole.USER, content=message.text))
        query_count += 1
        await message.answer(f'Запрос №{query_count} отправлен!🐈‍', reply_markup=klav)
        if query_count >= 10:
            await message.answer(f'У меня {query_count} запросов в памяти.'
                                 '\nРекомендую очистить её для экономии токенов и оптимизации работы!🐱', reply_markup=klav)
        response = giga.chat(chatik)
        chatik.messages.append(response.choices[0].message)
    return await message.answer(response.choices[0].message.content), await state.clear()

async def on_startup():
    global last_start_time
    last_start_time = dt.datetime.now(pytz.utc)
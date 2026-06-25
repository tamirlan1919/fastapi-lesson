from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.inline import main_menu_kb
from services.tracker_api import login, create_task, get_tasks
from state import AddTaskFSM
import logging

logger = logging.Logger(__name__)
router = Router()
user_sessions: dict[int, str] = {} #Хранить JWT


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    logger.info(f'User {user.id} {user.username} stated bot')
    await message.answer(
        f'Привет {user.first_name}! \n'
        'Я помогу управлять задачами Tracker\n'
        'Сначала войди в аккаунт \n',
        reply_markup=main_menu_kb()
    )


@router.message(Command('login'))
async def cmd_login(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer('Формат /login username password')
        return
    _, username, password = parts

    try:
        await message.delete()

    except Exception:
        pass

    token = await login(username, password)
    print(token)
    if token:
        user_sessions[message.from_user.id] = token
        await message.answer(f'Авторизован как {username}')
    else:
        await message.answer('Неверный username or password')


@router.message(Command('logout'))
async def cmd_logout(message: Message):
    user_sessions.pop(message.from_user.id, None)
    await message.answer('Сессия завершена, войдите снова')


@router.message(Command('tasks'))
async def cmd_tasks(message: Message):
    token = user_sessions.get(message.from_user.id)
    if not token:
        await message.answer('Сначала войди: /login username password')
        return
    tasks = await get_tasks(token)
    if tasks is None or tasks == []:
        await message.answer('Задач пока нет. Добавить задачу /add')
    done = sum(1 for t in tasks if t['is_done'])
    await message.answer(
        f'Задачи {len(tasks)} шт. Выполнено {done}\n'
        'Нажми на задачу чтобы отметить ее выполенной'
    )


@router.message(Command('add'))
async def cmd_add(message: Message, state: FSMContext):
    token = user_sessions.get(message.from_user.id)
    if not token:
        await message.answer('Сначала войди: /login username password')
        return
    await state.set_state(AddTaskFSM.waiting_title)
    await message.answer('Введите название задачи')


@router.message(AddTaskFSM.waiting_title)
async def add_get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTaskFSM.waiting_priority)
    await message.answer('Выбери приоритет от 1 до 5')


@router.message(AddTaskFSM.waiting_priority)
async def add_get_priority(message: Message, state: FSMContext):
    token = user_sessions.get(message.from_user.id)
    priority = int(message.text)
    data = await state.get_data()
    print(data)
    title = data['title']
    await state.clear()
    task = await create_task(token, title, priority)
    if task:
        await message.answer('Задача создана')
    else:
        await message.answer('Ошибка создания задачи')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random
import string
from db_utils import init_db, save_user_data, load_user_data, save_used_referral_code, load_used_referral_codes, load_all_user_data

# Initialize the database
init_db()

# Словарь для хранения ID сообщений и фотографий
message_data = {}

# Список разрешенных пользователей
allowed_users = [583969795]  # Замените на ID разрешенных пользователей

# Функция генерации уникального реферального кода
def generate_referral_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Функция для получения главного меню
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Реферальная программа", callback_data='referrals')],
        [InlineKeyboardButton("Буст", callback_data='boost')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для получения меню заданий
def get_tasks_menu():
    keyboard = [
        [InlineKeyboardButton("Подписка на канал.Награда: 5000$FP", callback_data='task_subscribe')],
        [InlineKeyboardButton("Пригласить 1 друга.Награда: 1000$FP", callback_data='task_invite_1')],
        [InlineKeyboardButton("Пригласить 5 друзей.Награда: 2000$FP", callback_data='task_invite_5')],
        [InlineKeyboardButton("Пригласить 10 друзей.Награда: 5000$FP", callback_data='task_invite_10')],
        [InlineKeyboardButton("Пригласить 50 друзей.Награда: 20000$FP", callback_data='task_invite_50')],
        [InlineKeyboardButton("Пригласить 100 друзей.Награда: 50000$FP", callback_data='task_invite_100')],
        [InlineKeyboardButton("Приписка в нике $FP.Награда: 10000$FP", callback_data='task_nickname')],
        [InlineKeyboardButton("Назад", callback_data='main_menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для удаления предыдущих сообщений и фотографий
async def delete_previous_messages(context, chat_id, user_id):
    if user_id in message_data:
        for message_id in message_data[user_id]:
            try:
                await context.bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"Error deleting message: {e}")
        message_data[user_id] = []

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    args = context.args

    user_data = load_user_data(user_id)
    if not user_data:
        user_data = {
            'username': username,
            'balance': 0,
            'referrals': 0,
            'referral_code': generate_referral_code(),
            'boost_claimed': False,
            'tasks': {
                'subscribe': False,
                'invite_1': False,
                'invite_5': False,
                'invite_10': False,
                'invite_50': False,
                'invite_100': False,
                'nickname': False,
            }
        }
        save_user_data(user_id, user_data)

    if args:
        ref_code = args[0]
        used_referral_codes = load_used_referral_codes()
        if ref_code not in used_referral_codes:
            used_referral_codes[ref_code] = set()

        if user_id not in used_referral_codes[ref_code]:
            for uid, data in load_all_user_data().items():
                if data['referral_code'] == ref_code and uid != user_id:
                    data['referrals'] += 1
                    data['balance'] += 1000
                    save_user_data(uid, data)
                    used_referral_codes[ref_code].add(user_id)
                    save_used_referral_code(ref_code, user_id)
                    break

    reply_markup = get_main_menu()
    main_message = ("""
    👋 Добро пожаловать в FootPunch bot!
    Бот, с помощью которого вы сможете детальнее ознакомиться с концепцией игры и получить преимущество над будущими игроками!

    ⚽ Что такое FootPunch?
    FootPunch - новая и первая p2e игра на основе Ton про футбол!
    Собирайте команду, тренируйте игроков и соревнуйтесь с другими пользователями!
    В данный момент игра находится в разработке и требует максимум вашего внимания.

    🤔 Для чего мне играть в это?
    Фишка нашего проекта - соревновательная составляющая.
    Геймплей связан с прокачкой игроков выбраного вами клуба, тренировками и pvp противостояними.
    Основная валюта игры - $FP, ваш способ заполучить преимущество над другими игроками и доминировать на поле!
    """
    )
    
    # Отправка изображения и текста в одном сообщении
    photo_message = await update.message.reply_photo(photo=open('main.jpg', 'rb'), caption=main_message, reply_markup=reply_markup)

    # Сохранение ID сообщений
    message_data[user_id] = [photo_message.message_id]

# Обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Отвечаем на запрос как можно раньше
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if query.data == 'balance':
        keyboard = [[InlineKeyboardButton("Назад", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        user_data = load_user_data(user_id)
        await context.bot.send_photo(chat_id=chat_id, photo=open('balance.jpg', 'rb'), caption=f"💲Ваш баланс: {user_data['balance']} $FP\n\n 💸Чтобы увеличить ваш баланс выполняйте различные активности во вкладке Буст, а так же приглашайте своих друзей.", reply_markup=reply_markup)
    elif query.data == 'referrals':
        user_data = load_user_data(user_id)
        referral_code = user_data['referral_code']
        referral_link = f"https://t.me/FootPunch_bot?start={referral_code}"
        keyboard = [[InlineKeyboardButton("Назад", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=chat_id, photo=open('referrals.jpg', 'rb'), caption="🔗Реферальная программа:\n\n""Приглашай друзей и получи вознаграждение в виде:1000 $FP за каждого друга\n""Чем больше друзей ты пригласишь - тем выше твоя награда!\n\n"f"Количество ваших рефералов: {user_data['referrals']}\nВаша реферальная ссылка: {referral_link}", reply_markup=reply_markup)
    elif query.data == 'boost':
        keyboard = [
            [InlineKeyboardButton("К заданиям", callback_data='tasks_menu')],
            [InlineKeyboardButton("Назад", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        boost_message = (
            "🚀 Получение токена $FP в начале игры предоставляет вам уникальное преимущество перед другими игроками. "
        "После релиза игры бонусы за приглашенных друзей больше начисляться не будут, так что не упустите свой шанс!\n\n"
        "Чтобы заработать токены $FP, вам нужно:\n\n"
        "1) Подписаться на наш канал.\n"
        "2) Пригласить друзей. За каждого нового игрока, который зарегистрируется по вашей ссылке, вы получите 1.000 $FP а также дополнительные награды.\n\n"
        "⚠️ Не забудьте: после выхода игры эта акция прекратит своё действие.\n\n"
        "🚀 Кнопка 'Буст' позволит вам заработать до 93.000 $FP за выполнение различных заданий и миссий.\n\n"
        "🔗 Приглашайте друзей с помощью вашей уникальной реферальной ссылки и накапливайте токены $FP для еще более захватывающего игрового опыта."
        )
        await context.bot.send_photo(chat_id=chat_id, photo=open('boost.jpg', 'rb'), caption=boost_message, reply_markup=reply_markup)
    elif query.data == 'tasks_menu':
        reply_markup = get_tasks_menu()
        await context.bot.send_message(chat_id=chat_id, text="Выберите задание:", reply_markup=reply_markup)
    elif query.data.startswith('task_'):
        task_handlers = {
            'task_subscribe': "Для выполнения этого задания вам нужно подписаться на наш канал: https://t.me/footpunch",
            'task_invite_1': "Для выполнения этого задания вам нужно пригласить одного друга.",
            'task_invite_5': "Для выполнения этого задания вам нужно пригласить 5 друзей.",
            'task_invite_10': "Для выполнения этого задания вам нужно пригласить 10 друзей.",
            'task_invite_50': "Для выполнения этого задания вам нужно пригласить 50 друзей.",
            'task_invite_100': "Для выполнения этого задания вам нужно пригласить 100 друзей.",
            'task_nickname': "Поставьте в ник приписку $FP.",
        }
        task_description = task_handlers.get(query.data, "Задание не найдено.")
        keyboard = [
            [InlineKeyboardButton("Проверить", callback_data=f'check_{query.data}')],
            [InlineKeyboardButton("Назад", callback_data='tasks_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=task_description, reply_markup=reply_markup)
    elif query.data.startswith('check_task_'):
        task_check_handlers = {
            'check_task_subscribe': check_task_subscribe,
            'check_task_invite_1': lambda uid, q, c: check_task_invite(uid, 1, 1000, q, c),
            'check_task_invite_5': lambda uid, q, c: check_task_invite(uid, 5, 2000, q, c),
            'check_task_invite_10': lambda uid, q, c: check_task_invite(uid, 10, 5000, q, c),
            'check_task_invite_50': lambda uid, q, c: check_task_invite(uid, 50, 20000, q, c),
            'check_task_invite_100': lambda uid, q, c: check_task_invite(uid, 100, 50000, q, c),
            'check_task_nickname': check_task_nickname,
        }
        task_check_handler = task_check_handlers.get(query.data)
        if task_check_handler:
            await task_check_handler(user_id, query, context)
    elif query.data == 'main_menu':
        reply_markup = get_main_menu()
        main_message = ("""
    👋 Добро пожаловать в FootPunch bot!
    Бот, с помощью которого вы сможете детальнее ознакомиться с концепцией игры и получить преимущество над будущими игроками!

    ⚽ Что такое FootPunch?
    FootPunch - новая и первая p2e игра на основе Ton про футбол!
    Собирайте команду, тренируйте игроков и соревнуйтесь с другими пользователями!
    В данный момент игра находится в разработке и требует максимум вашего внимания.

    🤔 Для чего мне играть в это?
    Фишка нашего проекта - соревновательная составляющая.
    Геймплей связан с прокачкой игроков выбраного вами клуба, тренировками и pvp противостояними.
    Основная валюта игры - $FP, ваш способ заполучить преимущество над другими игроками и доминировать на поле!
    """
    )
    
        await context.bot.send_photo(chat_id=chat_id, photo=open('main.jpg', 'rb'), caption=main_message, reply_markup=reply_markup)

    # Сохранение ID новых сообщений
    message_data[user_id] = [query.message.message_id]

# Функция проверки подписки на канал
async def check_task_subscribe(user_id, query, context):
    user_data = load_user_data(user_id)
    if not user_data['tasks']['subscribe']:
        if await check_subscription(context, user_id):
            user_data['balance'] += 5000
            user_data['tasks']['subscribe'] = True
            save_user_data(user_id, user_data)
            await context.bot.send_message(chat_id=query.message.chat_id, text="Подписка подтверждена! На ваш баланс добавлено 5000 $FP.", reply_markup=get_tasks_menu())
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Вы не подписаны на канал.", reply_markup=get_tasks_menu())
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Вы уже выполнили это задание.", reply_markup=get_tasks_menu())

# Функция проверки приглашенных друзей
async def check_task_invite(user_id, required_referrals, reward, query, context):
    user_data = load_user_data(user_id)
    task_name = f'invite_{required_referrals}'
    if not user_data['tasks'][task_name]:
        if user_data['referrals'] >= required_referrals:
            user_data['balance'] += reward
            user_data['tasks'][task_name] = True
            save_user_data(user_id, user_data)
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"Задание выполнено! На ваш баланс добавлено {reward} $FP.", reply_markup=get_tasks_menu())
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"Задание не выполнено. У вас недостаточно приглашенных друзей.", reply_markup=get_tasks_menu())
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Вы уже выполнили это задание.", reply_markup=get_tasks_menu())

# Функция проверки приписки в нике
async def check_task_nickname(user_id, query, context):
    user_data = load_user_data(user_id)
    if not user_data['tasks']['nickname']:
        if 'FP' in user_data['username']:
            user_data['balance'] += 10000
            user_data['tasks']['nickname'] = True
            save_user_data(user_id, user_data)
            await context.bot.send_message(chat_id=query.message.chat_id, text="Задание выполнено! На ваш баланс добавлено 10000 $FP.", reply_markup=get_tasks_menu())
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Задание не выполнено. У вас нет приписки FP в нике.", reply_markup=get_tasks_menu())
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Вы уже выполнили это задание.", reply_markup=get_tasks_menu())

# Обработчик команды /list_users для просмотра всех пользователей
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in allowed_users:
        await update.message.reply_text("У вас нет прав для использования этой команды.")
        return

    all_user_data = load_all_user_data()
    if all_user_data:
        users_list = "\n".join([f"ID: {user_id}, Username: {data['username']}, Referrals: {data['referrals']}" for user_id, data in all_user_data.items()])
        await update.message.reply_text(f"Список всех пользователей:\n{users_list}")
    else:
        await update.message.reply_text("Пользователи не найдены.")

# Обработчик текстовых сообщений для команды list_users_footpunchscambot123321&
async def handle_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.strip() == "list_users_footpunchscambot123321&":
        await list_users(update, context)

# Функция проверки подписки
async def check_subscription(context, user_id):
    channel_id = '@footpunch'  # Замените на ваше имя канала
    try:
        member_status = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member_status.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription status: {e}")
        return False

# Основная функция
def main() -> None:
    # Создание объекта Application и передача токена вашего бота
    app = ApplicationBuilder().token("7479177364:AAEFNEbwQjPE_uiSZnN02ewW-G4EBZM-aD0").build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^list_users_footpunchscambot123321&$'), handle_custom_command))
    app.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()

import time

import email_validate
import telebot_calendar
from telebot import *
from telebot_calendar import *
import config
import db_worker
from datetime import datetime, timedelta
import email_sender
import random
import sys
import inspect

bot = config.bot


class Main:
    user_language = 'ru'
    tg_user_id = None
    user_id = None
    message = None
    user_mail = None
    user_pass = None
    user_lvl = None
    end_time_base = None

    @staticmethod
    def reset():
        dic = vars(Main)
        for i in dic.keys():
            try:
                dic[i] = None
            except:
                None

    @staticmethod
    @bot.message_handler(commands=['admin'])
    def start_program(message):
        Main.reset()
        Main.tg_user_id = message.from_user.id
        Main.user_mail = '***'
        Main.user_id = db_worker.select_user_id(Main.user_mail)
        Main.user_pass = '***'
        Main.user_lvl = 'trial'
        Main.end_time_base = '2022-08-30'
        UserSubscribe.check_subscribe()

    @staticmethod
    @bot.message_handler(commands=['start'])
    def start_program(message):
        if Main.tg_user_id is None:
            Main.message = message
            Main.tg_user_id = message.from_user.id
            bot.send_message(Main.tg_user_id, 'Добро пожаловать в бота учёта финансов!\n'
                                              'Это удобное приложения для денежного учёта')
            Authorization.authorization_user(message)
        else:
            bot.send_message(Main.tg_user_id, 'Вы уже запустили бота!')
            UserSubscribe.check_subscribe()

    @staticmethod
    @bot.message_handler(commands=['exit'])
    def start_program(message):
        Main.reset()
        Main.message = message
        Main.tg_user_id = message.from_user.id
        Authorization.authorization_user(message)

    @staticmethod
    @bot.message_handler(commands=['retry'])
    def retry_authorization(message):
        print(f'Пользователь {Main.tg_user_id} запросил повторный ввод данных авторизации')
        Main.message = message
        Main.tg_user_id = message.from_user.id
        Authorization.authorization_user(message)


class Authorization:
    @staticmethod
    def authorization_user(message):
        bot.send_message(Main.message.from_user.id, text='Авторизация')
        print(f'Пользователю {Main.tg_user_id} предлагают пройти авторизацию')
        Authorization.registration_user(message)

    @staticmethod
    def registration_user(m):
        def get_mail(message):
            def check_mail_code(message):
                if str(code) == message.text:
                    bot.send_message(Main.tg_user_id, 'Код верный!')
                    bot.send_message(Main.tg_user_id, 'Вы не зарегистрированы!\n'
                                                      'Напишите ваш новый пароль:')
                    bot.register_next_step_handler(message, get_new_pass)
                    pass
                else:
                    if message.text == '/retry':
                        pass
                    bot.send_message(Main.tg_user_id, 'Для смены почты или пароля: /retry\n'
                                                      'Код неверный, повторите ввод:')
                    bot.register_next_step_handler(message, check_mail_code)
                    pass

            print(message.text)
            Main.user_mail = message.text
            if email_validate.validate(Main.user_mail):
                if db_worker.select_user_id(Main.user_mail) is not False:
                    bot.send_message(Main.tg_user_id, 'Напишите ваш пароль:')
                    print(f'Почта {Main.user_mail} пользователя {Main.tg_user_id} есть в базе')
                    bot.register_next_step_handler(message, get_pass)
                    pass
                else:
                    print(f'Почты {Main.user_mail} пользователя {Main.tg_user_id} нет в базе')
                    code = random.randint(1000, 9999)
                    email_sender.send_message(Main.user_mail, code)
                    bot.send_message(Main.tg_user_id, 'Мы отправили код подтверждения на почту.\n'
                                                      'Напишите его:')
                    bot.register_next_step_handler(message, check_mail_code)
                    pass
            else:
                bot.send_message(Main.tg_user_id, 'Неверный формат почты!\n'
                                                  'Повторите ввод:')
                bot.register_next_step_handler(message, get_mail)
                pass

        def get_pass(message):
            if message.text == '/retry':
                Main.retry_authorization(message)
                return None
            Main.user_pass = message.text
            Main.user_pass = db_worker.select_user_pass(Main.user_mail)
            if Main.user_pass == message.text:
                bot.send_message(Main.tg_user_id, f'Добро пожаловать, {Main.message.from_user.first_name}!')
                print(f'Пользователь {Main.tg_user_id} зашёл в аккаунт')
                UserSubscribe.check_subscribe()
            else:
                bot.send_message(Main.tg_user_id, f'Для смены почты или пароля: /retry\n'
                                                  f'Пароль не верный, повторите:')
                print(f'Пользователь {Main.tg_user_id} ошибся паролем при входе')
                bot.register_next_step_handler(message, get_pass)
                pass

        def get_new_pass(message):
            Main.user_pass = message.text
            if message.text == '/retry':
                Main.retry_authorization(message)
                return None
            print(f'Пользователь {Main.tg_user_id} написал пароль')
            bot.send_message(Main.tg_user_id, f'Повторите вод пароля для подтверждения:')
            bot.register_next_step_handler(message, check_pass)

        def check_pass(message):
            if message.text == '/retry':
                Main.retry_authorization(message)
                return None
            if Main.user_pass == message.text:
                print(f'Пользователь {Main.tg_user_id} повторил пароль успешно')
                db_worker.insert_t_user_tg(Main.tg_user_id, Main.user_mail)
                db_worker.insert_t_user_info(Main.user_mail, Main.user_pass, 'not_subscribe', 'null')
            else:
                print(f'Пользователь {Main.tg_user_id} повторил пароль не успешно')
                bot.send_message(Main.tg_user_id, f'Для смены почты или пароля: /retry\n'
                                                  f'Пароли не совпадают, повторите:')
                bot.register_next_step_handler(message, check_pass)
                pass
            print(f'Пользователь {Main.tg_user_id} зарегистрирован\n'
                  f'Его почта: {Main.user_mail}, его пароль: {Main.user_pass}')
            bot.send_message(Main.tg_user_id, f'Добро пожаловать! Вы зарегестрированы\n'
                                              f'Ваша почта {Main.user_mail}, ваш пароль: {Main.user_pass}')
            UserSubscribe.check_subscribe()

        print(f'Началась авторизация пользователя {Main.tg_user_id}')
        bot.send_message(Main.tg_user_id, 'Напишите вашу почту:')
        bot.register_next_step_handler(m, get_mail)


class UserSubscribe:
    @staticmethod
    def check_subscribe():
        Main.user_id = db_worker.select_user_id(Main.user_mail)
        Main.user_lvl, Main.end_time_base = db_worker.select_user_lvl(Main.user_mail)
        print(f'Пользователь: {Main.tg_user_id} запустил чат. level_user = {Main.user_lvl}')
        if Main.user_lvl == 'subscribed':
            if datetime.now().date() > Main.end_time_base:
                bot.send_message(Main.tg_user_id, f"Ваша подписка закончилась {format(Main.end_time_base, '%d/%m/%Y')}")
                UserSubscribe.subscribe_keyboard(trial_subscribe_flag=False)
            else:
                bot.send_message(Main.tg_user_id,
                                 f"Ваша подписка действует до {format(Main.end_time_base, '%d/%m/%Y')}")
                UserTransaction.main_keyboard()
        elif Main.user_lvl == 'trial':
            if datetime.now().date() > Main.end_time_base:
                print(f'Подписка пользователя {Main.tg_user_id} просрочена')
                bot.send_message(Main.tg_user_id,
                                 f"Ваш пробный период закончился {format(Main.end_time_base, '%d/%m/%Y')}\n")
                UserSubscribe.subscribe_keyboard(trial_subscribe_flag=False)
            else:
                bot.send_message(Main.tg_user_id,
                                 f"Ваш пробный период действует до {format(Main.end_time_base, '%d/%m/%Y')}")
                UserTransaction.main_keyboard()
        elif Main.user_lvl == 'not_subscribe':
            bot.send_message(Main.tg_user_id, f"Вы не подписаны.")
            UserSubscribe.subscribe_keyboard()

    @staticmethod
    def subscribe_keyboard(pay_subscribe_flag=True, trial_subscribe_flag=True):
        keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        pay_button = types.InlineKeyboardButton(text='Платная подписка', callback_data='pay_subscribe')
        trial_button = types.InlineKeyboardButton(text='Пробный период', callback_data='trial_subscribe')
        if pay_subscribe_flag and trial_subscribe_flag:
            keyboard.add(pay_button, trial_button)
        elif trial_subscribe_flag:
            keyboard.add(trial_button)
        else:
            keyboard.add(pay_button)
        bot.send_message(Main.message.from_user.id, text='Выбор подписки:', reply_markup=keyboard)
        print(f'Пользователю {Main.tg_user_id} предлагают подписку')

    @staticmethod
    def pay_subscribe():
        print(f'Пользователь {Main.tg_user_id} выбрал платный период')
        UserSubscribe.subscribe_keyboard()

    @staticmethod
    def trial_subscribe():
        end_time = datetime.now() + timedelta(weeks=1)
        end_time_message = format(end_time, '%d/%m/%Y')
        Main.end_time_base = format(end_time, '%Y-%m-%d')
        db_worker.change_lvl(Main.user_mail, 'trial', Main.end_time_base)
        bot.send_message(Main.message.from_user.id, text=f'Вы выбрали пробный период\n'
                                                         f'Он действует до {end_time_message}')

        print(f'Пользователь {Main.tg_user_id} выбрал пробный период')
        UserTransaction.main_keyboard()

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == 'pay_subscribe' or call.data == 'trial_subscribe')
    def callback_worker(call):
        bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
        if call.data == "pay_subscribe":
            # Authorization.login_user()
            None
        elif call.data == "trial_subscribe":
            UserSubscribe.trial_subscribe()
        else:
            bot.send_message(call.message.user.id, 'Повторите')


class UserTransaction:
    transaction_dict = None
    categories = None
    calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
    calendar = None

    @staticmethod
    def main_keyboard():
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        transaction_button = types.InlineKeyboardButton(text='Новая транзакция', callback_data='transaction')
        transaction_report_button = types.InlineKeyboardButton(text='Вывести транзакции',
                                                               callback_data='transaction_report')
        transaction_delete_button = types.InlineKeyboardButton(text='Удалить транзакцию',
                                                               callback_data='transaction_delete')
        transaction_category_delete_button = types.InlineKeyboardButton(text='Удалить категорию',
                                                                        callback_data='transaction_category_delete')
        exit_button = types.InlineKeyboardButton(text='Выйти из аккаунта', callback_data='exit')
        keyboard.add(transaction_button, transaction_delete_button,
                     transaction_category_delete_button,transaction_report_button,
                     exit_button)
        bot.send_message(Main.tg_user_id, text='Выберите:', reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == 'transaction' or
                                                  call.data == 'transaction_report' or
                                                  call.data == 'exit' or
                                                  call.data == 'cancel_transaction' or
                                                  call.data == 'transaction_delete' or
                                                  call.data == 'transaction_category_delete')
    def callback_worker(call):
        def start_transaction():
            UserTransaction.calendar = telebot_calendar.Calendar(
                language=RUSSIAN_LANGUAGE) if Main.user_language == 'ru' else telebot_calendar.Calendar()
            now = datetime.now()
            m = bot.send_message(Main.tg_user_id, text='Выберите дату операции:',
                                 reply_markup=UserTransaction.calendar.create_calendar(
                                     name=UserTransaction.calendar_1_callback.prefix,
                                     year=now.year,
                                     month=now.month
                                 ))

        @staticmethod
        @bot.callback_query_handler(
            func=lambda call: call.data.startswith(UserTransaction.calendar_1_callback.prefix)
        )
        def callback_inline(call: CallbackQuery):
            """
            Обработка inline callback запросов
            :param call:
            :return:
            """

            # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
            name, action, year, month, day = call.data.split(UserTransaction.calendar_1_callback.sep)
            # Processing the calendar. Get either the date or None if the buttons are of a different type
            date = UserTransaction.calendar.calendar_query_handler(
                bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
            )
            # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
            if action == "DAY":
                bot.send_message(
                    chat_id=call.from_user.id,
                    text=f"Дата транзакции: {date.strftime('%d.%m.%Y')}",
                    reply_markup=types.ReplyKeyboardRemove(),
                )
                UserTransaction.transaction_dict = {'date': date}
                print(f"Пользователь {Main.tg_user_id} выбрал дату: {date.strftime('%d.%m.%Y')}")
                date_transaction(call.message)
            elif action == "CANCEL":
                cancel_transaction(call.message)

        def date_transaction(m):
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            income_button = types.InlineKeyboardButton(text='Доход')
            expenditure_button = types.InlineKeyboardButton(text='Расход')
            cancel_button = types.InlineKeyboardButton(text='Отмена операции')
            keyboard.add(income_button, expenditure_button, cancel_button)
            m = bot.send_message(Main.tg_user_id, text='Выберите тип операции:', reply_markup=keyboard)
            bot.register_next_step_handler(m, type_transaction)

        def type_transaction(m):
            if m.text == 'Отмена операции':
                return cancel_transaction(m)
            if m.text not in ['Доход', 'Расход']:
                bot.send_message(Main.tg_user_id, 'Выберите из двух типов.')
                return date_transaction(m)
            print(f'Пользователь {Main.tg_user_id} записал type транзакции')
            UserTransaction.transaction_dict['type'] = m.text
            send_categories(m)

        def send_categories(m):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            UserTransaction.categories = db_worker.select_user_categories(Main.user_id,
                                                                          UserTransaction.transaction_dict['type'])
            for category in UserTransaction.categories:
                keyboard.add(types.InlineKeyboardButton(text=category))
            keyboard.add(types.InlineKeyboardButton(text='Отмена операции'))
            m = bot.send_message(Main.tg_user_id, text='Выберите категорию или запишите свою новую:',
                                 reply_markup=keyboard)
            bot.register_next_step_handler(m, category_transaction)

        def category_transaction(m):
            if m.text == 'Отмена операции':
                return cancel_transaction(m)
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text='Отмена операции', callback_data='cancel_transaction'))
            print(f'Пользователь {Main.tg_user_id} записал category транзакции')
            UserTransaction.transaction_dict['category'] = m.text
            m = bot.send_message(Main.tg_user_id, text=f'Вы выбрали категорию: {m.text}',
                                 reply_markup=types.ReplyKeyboardRemove())
            m = bot.send_message(Main.tg_user_id, text='Введите сумму операции:',
                                 reply_markup=keyboard)
            bot.register_next_step_handler(m, sum_transaction)

        def sum_transaction(m):
            if m.text == 'Отмена операции':
                return cancel_transaction(m)
            print(f'Пользователь {Main.tg_user_id} записал sum транзакции')
            try:
                user_sum = abs(float(m.text))
            except:
                bot.send_message(Main.tg_user_id, text='Вы ввели не сумму\n'
                                                       'Введите сумму операции:')
                return bot.register_next_step_handler(m, sum_transaction)
            UserTransaction.transaction_dict['sum'] = user_sum
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text='Отмена операции', callback_data='cancel_transaction'))
            bot.send_message(Main.tg_user_id, text='Введите описание операции:', reply_markup=keyboard)
            bot.register_next_step_handler(m, description_transaction)

        def description_transaction(m):
            if m.text == 'Отмена операции':
                return cancel_transaction(m)
            print(f'Пользователь {Main.tg_user_id} записал description транзакции')
            UserTransaction.transaction_dict['description'] = m.text
            UserTransaction.transaction_dict['user_id'] = Main.user_id
            transaction_id = db_worker.create_id('transaction_id', 't_transaction',
                                                 f'WHERE user_id = {UserTransaction.transaction_dict["user_id"]}')
            UserTransaction.transaction_dict['transaction_id'] = 1 if transaction_id == 0 else transaction_id
            if UserTransaction.transaction_dict['category'] not in UserTransaction.categories:
                db_worker.insert_t_user_category(Main.user_id,
                                                 UserTransaction.transaction_dict['type'],
                                                 UserTransaction.transaction_dict['category'])
                print(f'В базу добавлена категория {UserTransaction.transaction_dict["category"]} '
                      f'для пользователя {Main.tg_user_id}')
            db_worker.insert_t_transaction(UserTransaction.transaction_dict['user_id'],
                                           UserTransaction.transaction_dict['transaction_id'],
                                           UserTransaction.transaction_dict["date"].strftime("%Y-%m-%d"),
                                           UserTransaction.transaction_dict['type'],
                                           UserTransaction.transaction_dict['category'],
                                           UserTransaction.transaction_dict['sum'],
                                           UserTransaction.transaction_dict['description'])
            bot.send_message(Main.tg_user_id, text=f'Транзакция записана!\n'
                                                   f'Номер: {UserTransaction.transaction_dict["transaction_id"]}\n'
                                                   f'Дата: {UserTransaction.transaction_dict["date"].strftime("%d-%m-%Y")}\n'
                                                   f'Тип: {UserTransaction.transaction_dict["type"]}\n'
                                                   f'Категория: {UserTransaction.transaction_dict["category"]}\n'
                                                   f'Сумма: {UserTransaction.transaction_dict["sum"]}\n'
                                                   f'Описание: {UserTransaction.transaction_dict["description"]}\n',
                             reply_markup=types.ReplyKeyboardRemove())
            print(f'Пользователь {Main.tg_user_id} записал транзакцию')
            print(UserTransaction.transaction_dict)
            UserTransaction.transaction_dict = None
            UserTransaction.main_keyboard()

        def transaction_delete():
            def register_handler(message):
                if message.text == 'Отмена операции':
                    return cancel_transaction(m)
                elif message.text == 'Вывести транзакции':
                    bot.send_message(Main.tg_user_id, f'Вы выбрали вывести транзакции', reply_markup=types.ReplyKeyboardRemove())
                    return UserTransactionReport.start()
                db_worker.delete_t_transaction(Main.user_id,
                                               message.text.split(','))
                bot.send_message(Main.tg_user_id, f'Вы удалили транзакции: {message.text}')
                print(f'Пользователь {Main.tg_user_id} удалил транзакции: {message.text}')
                UserTransaction.main_keyboard()

            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(types.InlineKeyboardButton(text='Отмена операции'),
                         types.InlineKeyboardButton(text='Вывести транзакции'))
            m = bot.send_message(Main.tg_user_id, 'Введите номер транзакции, которую хотите удалить\n'
                                                  'или номера транзакций, которые хотите удалить, через запятую:',
                                 reply_markup=keyboard)
            bot.register_next_step_handler(m, register_handler)

        def transaction_category_delete():
            def register_handler_type(message):
                def register_handler_category(message):
                    if message.text == 'Отмена операции':
                        return cancel_transaction(message)
                    db_worker.delete_t_user_category(Main.user_id, type_cat, message.text)
                    bot.send_message(Main.tg_user_id, f'Вы удалили категорию : {message.text}', reply_markup=types.ReplyKeyboardRemove())
                    print(f'Пользователь {Main.tg_user_id} удалил категорию {message.text}')
                    UserTransaction.main_keyboard()
                if message.text == 'Отмена операции':
                    return cancel_transaction(message)
                if message.text not in ['Доход', 'Расход']:
                    bot.send_message(Main.tg_user_id, 'Выберите из двух типов.')
                    return register_handler_type(message)
                type_cat = message.text
                print(f'Пользователь {Main.tg_user_id} записал type транзакции для удаления категории')
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                UserTransaction.categories = db_worker.select_user_categories(Main.user_id,
                                                                              message.text)
                for category in UserTransaction.categories:
                    keyboard.add(types.InlineKeyboardButton(text=category))
                keyboard.add(types.InlineKeyboardButton(text='Отмена операции'))
                m = bot.send_message(Main.tg_user_id, text='Выберите категорию, которую хотите удалить:',
                                     reply_markup=keyboard)
                bot.register_next_step_handler(m, register_handler_category)

            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            income_button = types.InlineKeyboardButton(text='Доход')
            expenditure_button = types.InlineKeyboardButton(text='Расход')
            cancel_button = types.InlineKeyboardButton(text='Отмена операции')
            keyboard.add(income_button, expenditure_button, cancel_button)
            m = bot.send_message(Main.tg_user_id, text='Выберите тип операции:', reply_markup=keyboard)
            bot.register_next_step_handler(m, register_handler_type)

        if call.data == 'transaction':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            start_transaction()
        elif call.data == 'transaction_delete':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            transaction_delete()
        elif call.data == 'transaction_category_delete':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            transaction_category_delete()
        elif call.data == 'transaction_report':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            UserTransactionReport.start()
        elif call.data == 'exit':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            bot.send_message(call.message.chat.id, 'Нажми, чтоб подтвердить /exit')
        elif call.data == 'cancel_transaction':
            print(f'Пользователь {Main.tg_user_id} отменил запись транзакции')
            UserTransaction.transaction_dict = {}
            m = bot.send_message(Main.tg_user_id, text='Отмена операции', reply_markup=types.ReplyKeyboardRemove())
            bot.delete_message(m.chat.id, message_id=m.message_id)
            UserTransaction.main_keyboard()

        def cancel_transaction(m):
            print(f'Пользователь {Main.tg_user_id} отменил запись транзакции')
            UserTransaction.transaction_dict = {}
            m = bot.send_message(Main.tg_user_id, text='Отмена операции', reply_markup=types.ReplyKeyboardRemove())
            bot.delete_message(m.chat.id, message_id=m.message_id)
            UserTransaction.main_keyboard()


class UserTransactionReport:
    @staticmethod
    def start():
        print(f'Пользователь {Main.tg_user_id} открыл окно выбора вывода транзакции')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        transaction_button = types.InlineKeyboardButton(text='Вывести все транзакции',
                                                        callback_data='report_all_transaction')
        cancal_button = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_transaction_report')
        keyboard.add(transaction_button, cancal_button)
        bot.send_message(Main.tg_user_id, text='Выберите:', reply_markup=keyboard)

    @staticmethod
    def report_all_transaction():
        text = 'Транзакций пок нет'
        transactions = []
        in_sum = out_sum = 0.0
        for transaction in db_worker.select_user_transaction(Main.user_id):
            if transaction[3] == 'Доход':
                in_sum += float(transaction[5])
            else:
                out_sum += float(transaction[5])
            transactions.append(f'{transaction[1]}) {format(transaction[2], "%d-%m-%Y")}, {transaction[3]}, ' \
                                f'{transaction[4]}, {transaction[5]}, {transaction[6]}')
        if transactions:
            text = '\n'.join(transactions)
        bot.send_message(Main.tg_user_id, f'Все ваши транзакции:\n'
                                          f'{text}\n'
                                          f'Сумма доходов: {in_sum}\n'
                                          f'Сумма расходов: {out_sum}')
        print(f'Пользователь {Main.tg_user_id} вывел все свои транзакции')
        UserTransactionReport.start()

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == 'report_all_transaction' or
                                                  call.data == 'cancel_transaction_report')
    def callback_worker(call):
        if call.data == 'report_all_transaction':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            print(f'Пользователь {Main.tg_user_id} выбрал вывод всех своих транзакции')
            UserTransactionReport.report_all_transaction()
        elif call.data == 'cancel_transaction_report':
            bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
            print(f'Пользователь {Main.tg_user_id} отменил вывод транзакции')
            UserTransaction.main_keyboard()


def main():
    bot.polling(none_stop=True, interval=0)

    # 2) создать t_transaction (user_id, transaction_id, type, sum, description), select в него
    # 3) Сделать отслеживание пользователя не по tg_id, а по user_mail
    # 3) Прописать ввод дохода/расхода, выход, проверку подписки в Transaction.main_keyboard
    # 4) Прописать проверку почты по коду, проверку почты в бд и перенос на вход авторизацию
    # 5) Прописать Вход авторизации
    # 6) Прописать пробный период, его дату окончания
    # 7) Прописать ввод дохода/расхода
    # 8) Прописать платный период и транзакцию
    # 9) Прописать в UserSubscribe.subscribe_keyboard проверку и продление платной подписки

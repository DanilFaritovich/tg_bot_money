from telebot import *
from telebot.apihelper import ApiTelegramException
db_password = '***'
email_password = '***'
bot_mail = '***'

class Exception_Handler:
    def handle(self, e: Exception):
        # Here you can write anything you want for every type of exceptions
        if isinstance(e, ApiTelegramException):
            print(e)

bot = telebot.TeleBot('***', exception_handler=Exception_Handler())

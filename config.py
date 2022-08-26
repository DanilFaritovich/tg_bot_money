from telebot import *
from telebot.apihelper import ApiTelegramException
db_password = 'Danchiktv321'
email_password = 'Danchiktv123'
bot_mail = 'Finance.manager.dir.bot@gmail.com'

class Exception_Handler:
    def handle(self, e: Exception):
        # Here you can write anything you want for every type of exceptions
        if isinstance(e, ApiTelegramException):
            print(e)

bot = telebot.TeleBot('5772662850:AAFzWSJcWeoyT2XBbgJrrOgrs42bPiol_Y0', exception_handler=Exception_Handler())
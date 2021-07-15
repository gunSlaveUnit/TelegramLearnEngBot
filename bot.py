import turtle

import os

from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from settings import DB_URL, DB_PORT, DB_NAME


class Bot:
    def __init__(self, token):
        self.__token = token
        self.__updater = Updater(self.__token)
        self.__dispatcher = self.__updater.dispatcher
        self.__db_client = MongoClient(DB_URL, DB_PORT)
        self.__db = self.__db_client[DB_NAME]
        self.__create_handlers()

        self.__current_right_translate = ""

    def run(self):
        self.__updater.start_polling()
        self.__updater.idle()

    def __create_handlers(self):
        self.__dispatcher.add_handler(CommandHandler("start", self.__start))
        self.__dispatcher.add_handler(CommandHandler("learn", self.__learn))
        self.__dispatcher.add_handler(CommandHandler("help", self.__help))
        self.__dispatcher.add_handler(CommandHandler("progress", self.__progress))
        self.__dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), self.__check_translate))
        self.__dispatcher.add_handler(MessageHandler(Filters.command, self.__unknown))

    def __start(self, update, context):
        users = self.__db["users"]
        user_id = update.message.chat.id
        if not users.find_one({"id": user_id}):
            users.insert_one({"id": user_id,
                              "progress": 1})
        update.message.reply_text(text=f"Hello, {update.message.chat.first_name}!")

    def __learn(self, update, context):
        words = self.__db["words"]
        users = self.__db["users"]

        current_word_id = users.find_one({"id": update.message.chat.id})["progress"]
        current_word = words.find_one({"id": current_word_id})
        word = current_word["word"]
        self.__current_right_translate = current_word["translate"]
        update.message.reply_text(text=word)

    def __check_translate(self, update, context):
        if update.message.text.lower() == self.__current_right_translate.lower():
            update.message.reply_text(text="OK")
            users = self.__db["users"]
            new_word_number = users.find_one({"id": update.message.chat.id})["progress"] + 1
            users.update_one({"id": update.message.chat.id}, {"$set": {"progress": new_word_number}})
            self.__learn(update, context)
        else:
            update.message.reply_text(text="NOTOK")
            self.__learn(update, context)

    @staticmethod
    def __help(update, context):
        update.message.reply_text('Help!')

    def __progress(self, update, context):
        words = self.__db["words"]
        users = self.__db["users"]

        amount_learned_words = users.find_one({"id": update.message.chat.id})["progress"]
        amount_words = words.find().sort("id", -1).limit(1)[0]["id"]

        update.message.reply_text(text=f"Вы выучили {amount_learned_words} "
                                       f"из {amount_words} слов. Продолжайте в том же духе!")

    @staticmethod
    def __unknown(update, context):
        update.message.reply_text(text="Sorry, but I don't understand this command")

    def __fill_the_database_from_file_with_translated_words(self, filename):
        words = self.__db['words']
        with open(os.path.realpath(filename), 'r', encoding='utf8') as f:
            word_number = 1
            for line in f.readlines():
                word_with_translate = line.split(sep=' ')
                words.insert_one({"id": word_number,
                                  "word": word_with_translate[0],
                                  "translate": word_with_translate[1][:len(word_with_translate[1]) - 1]})
                word_number += 1

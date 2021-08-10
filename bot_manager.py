import os

import random
from random import randrange
import textblob
from textblob import TextBlob
from telegram.ext import Updater, handler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from config import Config
from interpreter import Interpreter
from notion_client import NotionClient

config = Config()
config.load()

start_message = "Hi"

hi_keywords = ["hola", "buenas", "holi", "hi"]
option_keywords = ["otra", "otro", "siguente"]
thanks_keywords = ["gracias"]

# Define Intepreter class
interpreter = Interpreter("spanish")

# Define Notion Client class
notion = NotionClient()

# Commands Functions
def start_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

# Message Functions
def unknowns_message(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


class Translator:
    def __init__(self, lang):
        self.lang = lang

    def translate(self, text):
        blob = TextBlob(text)
        return blob.translate(to=self.lang)


class Bot:
    def __init__(self):
        self.updater = Updater(token=config.get("TELEGRAM", "BOT_TOKEN"), use_context=True)
        self.dispatcher = self.updater.dispatcher

        self._define_basic_commands()
        self._define_basic_messages()

        # Meals
        self.meal_options = []

        # Get all Notion available categories/filters
        self.properties = self.get_notion_available_categories_filters()

        # Always the final defined command/message
        self.dispatcher.add_handler(MessageHandler(Filters.command, unknowns_message))

    def _set_random_option(self):
        return random.randint(0, len(self.meal_options) - 1)

    def _manage_meal_options(self, filter_dict):
        # Build filter query dict
        filter_query = {"filter": {}}
        for prop in filter_dict:
            filter_query["filter"]["property"] = prop
            filter_query["filter"]["select"] = {}
            filter_query["filter"]["select"]["equals"] = filter_dict[prop][0]

        # Get database options
        db_options = notion.get_database_by_filter(filter_query)
        if not db_options:
            return False
        if db_options:
            for result in db_options["results"]:
                self.meal_options.append(
                    result["properties"][list(result["properties"].keys())[-1]]["title"][0]["plain_text"]
                    )
        return True
         
    def filter_message(self, update, context):
        # Basic filter
        msg = update.message.text
        words = [word.lower() for word in msg.split()]

        filtered = False
        for w in words:
            if w in option_keywords:
                filtered = True
                if self.meal_options:
                    meal_option_index = self._set_random_option()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.meal_options[meal_option_index])
            elif w in hi_keywords:
                filtered = True
                context.bot.send_message(chat_id=update.effective_chat.id, text=hi_keywords[random.randint(0, len(hi_keywords) - 1)])
            elif w in thanks_keywords:
                filtered = True
                context.bot.send_message(chat_id=update.effective_chat.id, text="Gracias a ti, estoy disponible siempre que necesites")
            else:
                pass

        if not filtered:
            # Translate message keywords
            en_translator = Translator("en")
            input_key_words = interpreter.tokenize_filter_process(update.message.text)
            input_key_words_translated = []
            for word in input_key_words:
                try:
                    input_key_words_translated.append(en_translator.translate(word).string)
                except textblob.exceptions.NotTranslated:
                    pass

            # Find key-word matches
            only_one_option = {}
            for opt in self.properties:
                if self.properties[opt]["type"] == "select":
                    only_one_option[opt] = self.properties[opt]["options"]
            
            keywords_matches = []
            for word in input_key_words_translated:
                if word in only_one_option[list(only_one_option.keys())[0]]:
                    keywords_matches.append(word)
            if not keywords_matches:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Elige un tipo de cocina para que pueda ayudarte")
            else:
                filter_dict = {}
                filter_dict[list(only_one_option.keys())[0]] = keywords_matches
                
                # Define meal options
                if not self._manage_meal_options(filter_dict):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="No he encontrado ningun plato con ese filtro")
                else:
                    # Show meal options
                    meal_option_index = self._set_random_option()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.meal_options[meal_option_index])

    def _define_basic_commands(self):
        # Start command
        start_handler = CommandHandler('start', start_command)
        self.dispatcher.add_handler(start_handler)

    def _define_basic_messages(self):
        filter_message_handler = MessageHandler(Filters.text & (~Filters.command), self.filter_message)
        self.dispatcher.add_handler(filter_message_handler)

    def get_notion_available_categories_filters(self):
        db = notion.get_database()
        categories = ["select", "multi_select"]

        properties_dict = {}
        db_properties = db["properties"]
        for prop in db_properties:
            if db_properties[prop]["type"] in categories:
                properties_dict[prop] = {}
                properties_dict[prop]["type"] = db_properties[prop]["type"]
                options = []
                for opt in db_properties[prop][db_properties[prop]["type"]]["options"]:
                    options.append(opt["name"])
                properties_dict[prop]["options"] = options
        return properties_dict


bot = Bot()
bot.updater.start_polling()

import telebot

TOKEN = "8382678188:AAHTjWMwsltMC6IaOr5HLGL-7zLQ03ZpUKM" #I removed my token, so it will not work in your code
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "I am here to help you, Choose a book ")

bot.infinity_polling(skip_pending=True)

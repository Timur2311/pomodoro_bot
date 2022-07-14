#!/usr/bin/env python

# pylint: disable=unused-argument, wrong-import-position

# This program is dedicated to the public domain under the CC0 license.


"""

Simple Bot to send timed Telegram messages.


This Bot uses the Application class to handle the bot and the JobQueue to send

timed messages.


First, a few handler functions are defined. Then, those functions are passed to

the Application and registered at their respective places.

Then, the bot is started and runs until we press Ctrl-C on the command line.


Usage:

Basic Alarm Bot example, sends a message after a set time.

Press Ctrl-C on the command line or send a signal to the process to stop the

bot.

"""


import logging


from telegram import InlineKeyboardButton, __version__ as TG_VER
 
from telegram import ReplyKeyboardMarkup,InlineKeyboardButton

from telegram.ext import CallbackContext

try:

    from telegram import __version_info__

except ImportError:

    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]


if __version_info__ < (20, 0, 0, "alpha", 1):

    raise RuntimeError(

        f"This example is not compatible with your current PTB version {TG_VER}. To view the "

        f"{TG_VER} version of this example, "

        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"

    )

from telegram import Update

from telegram.ext import Application, CommandHandler, ContextTypes


# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)



# Define a few command handlers. These usually take the two arguments update and

# context.

# Best practice would be to replace context with an underscore,

# since context is an unused local variable.

# This being an example and not having context present confusing beginners,

# we decided to have it present as context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""  
    reply_keyboard = [
        ["/5", "/15", "/25"], 
        ["/set", "cancel", "/stats" ]
        ]        
    chat_id = update.effective_message.chat_id
    await context.bot.send_message(
        chat_id,
        text="Quyidagilardan birortasini tanlang yoki /set buyrug'i orqali xohlagan vaqtingizni belgilang",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
    )
async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Send the alarm message."""

    job = context.job

    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")



def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:

    """Remove job with given name. Returns whether job was removed."""

    current_jobs = context.job_queue.get_jobs_by_name(name)

    print(current_jobs)
    
    if not current_jobs:

        return False

    for job in current_jobs:
        print(job.next_t)
        job.schedule_removal()

    return True




async def callback_30(context: CallbackContext):
    await context.bot.send_message(chat_id=1497367630, text='A single message with 20s delay')


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Add a job to the queue."""

    chat_id = update.effective_message.chat_id

    try:

        # args[0] should contain the time for the timer in seconds

        due = float(context.args[0])

        if due < 0:

            await update.effective_message.reply_text("Kechirasiz, biz kelajakka qayta olmaymiz!")

            return


        job_removed = remove_job_if_exists(str(chat_id), context)

        setting_time = context.job_queue.run_once(callback_30, due)
        print(f"setting_time_object---->{setting_time}\n\n type_of_object----{type(setting_time)}")
        

        text = "Pomodoro muvaqqiyatli o'rnatildi!"

        if job_removed:

            text += " Eski pomodor o'chirildi."

        button = [[
        InlineKeyboardButton("Qancha qolganligini bilish", callback_data = "show_timer" ),
    ]]
        
        await update.effective_message.reply_text(text)


    except (IndexError, ValueError):

        await update.effective_message.reply_text("Usage: /set <seconds>")



async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Remove the job if the user changed their mind."""

    chat_id = update.message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)

    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."

    await update.message.reply_text(text)



def main() -> None:

    """Run bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder().token("").build()


    # on different commands - answer in Telegram

    application.add_handler(CommandHandler(["start", "help"], start))

    application.add_handler(CommandHandler("set", set_timer))

    application.add_handler(CommandHandler("unset", unset))


    # Run the bot until the user presses Ctrl-C

    application.run_polling()



if __name__ == "__main__":

    main()
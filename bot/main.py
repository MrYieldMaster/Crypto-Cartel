from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from telegram import error as tg_error
from shop import display_shop, handle_shop_callback, buy_backpack, buy_health_pack
from dat_manager import get_user_data, initialize_user
from travel import list_cities, travel_callback, restart_game
from prices import get_current_prices
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from loan import take_loan_command, repay_loan_command, check_due_loans
import logging
from dotenv import load_dotenv
import os
import asyncio


load_dotenv() 

# Importing the necessary functionalities from other modules
from events import ask_drug_to_buy, handle_buy_callback, ask_drug_to_sell, handle_sell_callback, random_event, confirm_buy, confirm_sell
from daily import daily_bonus
from leaderboard import leaderboard_command

# Use an environment variable to store your TOKEN securely
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_logger = logging.getLogger('telegram')
telegram_logger.setLevel(logging.DEBUG)

async def periodic_loan_check():
    while True:
        check_due_loans()
        await asyncio.sleep(60*60)  # Sleep for 1 hours



# Handler for the /start command
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id 
    user_name = update.message.from_user.first_name  # Get the user's name
    
    welcome_message = """
    Welcome to Crypto Cartel! 🌍
    Dive deep into the world of cryptos and cartels. Rule the streets, 
    trade in the shadows, and rise to the top. But always remember: trust no one.
    Type /start or /help to get started.
    """
    
    custom_keyboard = [['/status', '/leaderboard', '/loan'], 
                   ['/buy', '/sell', '/shop'],
                   ['/take_loan', '/repay_loan', '/buyhealthpack'],
                   ['/backpacks', '/daily','/travel']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup)

    
    if not get_user_data(user_id):
        initialize_user(user_id, user_name)
        update.message.reply_text("Welcome! Your profile has been created.")
    else:
        update.message.reply_text("Welcome back!")

    
def display_options(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Buy", callback_data='buy'), 
         InlineKeyboardButton("Sell", callback_data='sell')],
        [InlineKeyboardButton("Shop", callback_data='shop'), 
         InlineKeyboardButton("Travel", callback_data='travel')],
        [InlineKeyboardButton("Loan", callback_data='loan')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print(reply_markup)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

# Handler for the /help command
def help_command(update, context):
    help_text = """
/start - 🚀 Begin your drug empire adventure!
/help - ❓ Displays this help message.
/buy - 🛍️ Start the buying process for drugs.
/sell - 💼 Start the selling process for drugs.
/status - ℹ️ Check your current status, cash, inventory, and more.
/leaderboard - 🏆 See the top drug dealers in the game.
/daily - 📆 Claim your daily reward.
/confirmbuy - ✅ Confirm your drug purchase.
/confirmsell - ✅ Confirm your drug sale.
/buyhealthpack - 💉 Purchase a health pack to restore health.
/backpacks - 🎒 Purchase a new backpack to increase inventory space.
/shop - 🏬 Visit the shop for items.
/travel - 🌍 Travel between cities.
/options - ⚙️ See game options and settings.
/restart - 🔄 Restart your game.
/take_loan - 💵 Take a loan.
/repay_loan - 💰 Repay your loan.
/loan - 🧾 Check your loan status.
    """
    update.message.reply_text(help_text)

    
def error_handler(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    try:
        raise context.error
    except tg_error.Unauthorized:
        # remove update.message.chat_id from conversation list
        pass
    except tg_error.BadRequest:
        # handle malformed requests - read more below!
        pass
    except tg_error.TimedOut:
        # handle slow connection problems
        pass
    except tg_error.NetworkError:
        # handle other connection problems
        pass
    except tg_error.ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        pass
    except tg_error.TelegramError:
        # handle all other telegram related errors
        pass
    
    update.message.reply_text("Sorry, something went wrong. Please try again.")


    
def status(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    # Only initialize a new user if they don't exist in our 'database'
    if user_data is None:
        initialize_user(user_id)
        user_data = get_user_data(user_id)

    current_city = user_data['city']
    print(f"City data for user {user_id}: {user_data['city']}")

    city_prices = get_current_prices(user_data["city"])
    prices_status = "\n".join([f"💊 <b>{drug}</b>: {price}$" for drug, price in city_prices.items()])

    # Handle empty inventory
    if user_data["inventory"]:
        inventory_status = "\n".join([f"💊 <b>{drug}</b>: {amount}" for drug, amount in user_data["inventory"].items()])
    else:
        inventory_status = "🚫 Empty"
        
    current_day = user_data['day']
    
    loan_status = f"💸 <b>🏦 Loan Outstanding</b>: <i>${user_data['loan']}</i>\n" if user_data['loan'] > 0 else ""


    message = (
        f"<b>🌆 Current City</b>: <i>{user_data['city']}</i>\n"
        f"<b>💰 Cash</b>: <i>${user_data['cash']}</i>\n"
        f"<b>🩸 Health</b>: <i>{user_data['health']}%</i>\n"
        f"<b>📆 Day</b>: <i>{current_day}</i>\n"
        f"{loan_status}"
        f"\n<b>📈 Drug Prices</b>:\n"
        f"{prices_status}\n"
        f"\n<b>🎒 Inventory</b>:\n"
        f"{inventory_status}\n"
        
    )
    update.message.reply_text(message, parse_mode="HTML")


   
def daily_command(update: Update, context: CallbackContext) -> None:
    """Handle the /daily command to distribute daily bonuses."""
    user_id = update.message.from_user.id
    message = daily_bonus(user_id)
    if message:
        update.message.reply_text(message)
    else:
        update.message.reply_text("You've already claimed your daily bonus today. Come back tomorrow!")

def loan_info(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    
    if 'loan' in user_data and user_data['loan'] > 0:
        update.message.reply_text(f"You currently owe ${user_data['loan']} to the loan shark.")
    else:
        update.message.reply_text("You have no outstanding loans. Keep it up!")


# Main function to initialize the bot and register handlers
def main() -> None:
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher

    # Command handlerscd
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('buy', ask_drug_to_buy))
    dp.add_handler(CommandHandler('sell', ask_drug_to_sell))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CommandHandler('leaderboard', leaderboard_command))
    dp.add_handler(CommandHandler('daily', daily_command))
    dp.add_handler(CommandHandler('confirmbuy', confirm_buy))
    dp.add_handler(CommandHandler('confirmsell', confirm_sell))
    dp.add_handler(CommandHandler('buyhealthpack', buy_health_pack, pass_args=True))
    dp.add_handler(CommandHandler('backpacks', buy_backpack, pass_args=True))
    dp.add_handler(CommandHandler('shop', display_shop))
    dp.add_handler(CommandHandler('travel', list_cities))
    dp.add_handler(CommandHandler('options', display_options))
    dp.add_handler(CommandHandler('restart', restart_game))
    dp.add_handler(CommandHandler('take_loan', take_loan_command, pass_args=True))
    dp.add_handler(CommandHandler('repay_loan', repay_loan_command, pass_args=True))
    dp.add_handler(CommandHandler('loan', loan_info))




    dp.add_error_handler(error_handler)

    # Callback query handlers for inline buttons
    dp.add_handler(CallbackQueryHandler(handle_buy_callback, pattern='^buy_'))
    dp.add_handler(CallbackQueryHandler(handle_sell_callback, pattern='^sell_'))
    dp.add_handler(CallbackQueryHandler(handle_shop_callback, pattern='^shop_'))
    dp.add_handler(CallbackQueryHandler(travel_callback, pattern='^travel_'))


    loop = asyncio.get_event_loop()
    loop.create_task(periodic_loan_check())
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
 main()

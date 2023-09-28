from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from prices import get_current_prices
from dat_manager import get_user_data, update_user_data


# Assuming load_data() fetches user data from the database
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Shop module logger is working!")


BACKPACKS = {
    "small": {"price": 100, "capacity": 100},
    "medium": {"price": 500, "capacity": 200},
    "large": {"price": 1000, "capacity": 400}
}

HEALTH_PACKS = {
    "small": {"price": 200, "health_restore": 10},
    "medium": {"price": 500, "health_restore": 30},
    "large": {"price": 2000, "health_restore": 100}
}


def display_shop(update: Update, _: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🌿 Buy Drugs", callback_data='shop_drugs')],
        [InlineKeyboardButton("🎒 Backpacks", callback_data='shop_backpacks')],
        [InlineKeyboardButton("❤️ Health Packs", callback_data='shop_healthpacks')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('*Welcome to the Shop!*\nWhat would you like to buy today?', reply_markup=reply_markup, parse_mode='Markdown')


def handle_shop_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    logger.debug(f"Received callback: {query.data}")

    if query.data == 'shop_drugs':
        display_drug_menu(update, context)
    elif query.data == 'shop_backpacks':
        display_backpack_menu(update, context)
    elif query.data == 'shop_healthpacks':
        display_healthpack_menu(update, context)
    elif query.data.startswith('buy_healthpack_'):
        logger.debug("Inside buy_healthpack_ handler")
        pack_size = query.data.split('_')[-1]
        context.user_data['buying_healthpack'] = pack_size
        query.edit_message_text(f"How many {pack_size} health packs would you like to buy?")
        context.user_data['expecting'] = 'healthpack_amount'
    elif query.data.startswith('buy_'):
        logger.debug("Inside buy_ drug handler")
        drug_name = query.data.split('_')[1]
        context.user_data['buying'] = drug_name
        query.edit_message_text(f"How many units of {drug_name} would you like to buy?")
        context.user_data['expecting'] = 'drug_amount'
    elif query.data.startswith('buy_backpack_'):
        logger.debug("Inside buy_backpack_ handler")
        size = query.data.split('_')[-1]
        buy_backpack(update, context, size)
    elif query.data == 'back_to_shop':
        display_shop(update, context)





def display_drug_menu(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    user_data = get_user_data(user_id)
    city_prices = get_current_prices(user_data["city"])


    keyboard = [
        [InlineKeyboardButton(f"{drug} - {price}$", callback_data=f'buy_{drug}') for drug, price in city_prices.items()],
        [InlineKeyboardButton("Back to Shop", callback_data='back_to_shop')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.edit_message_text("Which drug would you like to buy?", reply_markup=reply_markup)
    else:
        update.message.reply_text("Which drug would you like to buy?", reply_markup=reply_markup)



def process_drug_purchase(update: Update, context: CallbackContext, drug, amount):
    user_data = get_user_data(update.message.from_user.id)
    city_prices = get_current_prices(user_data["city"])
    
    if drug not in city_prices:
        logger.error(f"Unknown drug {drug} for user {update.message.from_user.id}.")
        update.message.reply_text(f"Sorry, the drug {drug} is not available.")
        return

    drug_price = city_prices[drug]
    total_price = amount * drug_price

    if user_data["cash"] < total_price:
       update.message.reply_text(f"You don't have enough money! You need {total_price}$ but you have {user_data['cash']}$. Consider taking a loan using /take_loan <amount>.")
       return


    if user_data["backpack_capacity"] < amount:
        update.message.reply_text("You don't have enough space in your backpack!")
        return

    # Deduct money and add drugs to inventory
    user_data["cash"] -= total_price
    user_data["inventory"][drug] = user_data["inventory"].get(drug, 0) + amount

    update.message.reply_text(f"You bought {amount} units of {drug} for {total_price}$!")
    save_user_data(user_data)


def display_backpack_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(f"{size.capitalize()} - {data['price']}$", callback_data=f'buy_backpack_{size}') for size, data in BACKPACKS.items()],
        [InlineKeyboardButton("Back to Shop", callback_data='back_to_shop')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.edit_message_text("Upgrade your backpack:", reply_markup=reply_markup)
    else:
        update.message.reply_text("Upgrade your backpack:", reply_markup=reply_markup)

def buy_backpack(update, context):
    user_input = context.args
    
    if len(user_input) != 1:
        update.message.reply_text("Invalid format. Please use /buybackpack <small/medium/large>.")
        return

    pack_type = user_input[0]

    if pack_type not in BACKPACKS:
        update.message.reply_text("Unknown backpack type.")
        return

    total_cost = BACKPACKS[pack_type]["price"]

    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)

    if user_data["cash"] < total_cost:
        update.message.reply_text(f"You don't have enough money to buy a {pack_type} backpack.")
        return

    user_data["cash"] -= total_cost
    user_data["backpack_capacity"] = BACKPACKS[pack_type]["capacity"]

    update_user_data(user_id, user_data)

    update.message.reply_text(f"Successfully bought a {pack_type} backpack for ${total_cost}. Your backpack capacity is now {user_data['backpack_capacity']}.")

def display_healthpack_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(f"{size.capitalize()} - {data['price']}$", callback_data=f'buy_healthpack_{size}') for size, data in HEALTH_PACKS.items()],
        [InlineKeyboardButton("Back to Shop", callback_data='back_to_shop')]
    ]
    
    logger.debug("Displaying health pack menu...")

    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.edit_message_text("Choose a health pack:", reply_markup=reply_markup)
    else:
        update.message.reply_text("Choose a health pack:", reply_markup=reply_markup)

def buy_health_pack(update, context):
    user_input = context.args
    
    if len(user_input) != 2 or not user_input[1].isdigit():
        update.message.reply_text("Invalid format. Please use /buyhealthpack <small/medium/large> <amount>.")
        return

    pack_type, amount = user_input[0], int(user_input[1])

    if pack_type not in HEALTH_PACKS:
        update.message.reply_text("Unknown health pack type.")
        return

    total_cost = amount * HEALTH_PACKS[pack_type]["price"]

    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)

    if user_data["cash"] < total_cost:
        update.message.reply_text(f"You don't have enough money to buy {amount} {pack_type} health packs.")
        return

    user_data["cash"] -= total_cost
    user_data["health"] = min(100, user_data["health"] + amount * HEALTH_PACKS[pack_type]["health_restore"])

    update_user_data(user_id, user_data)

    update.message.reply_text(f"Successfully bought {amount} {pack_type} health packs for ${total_cost}. Your health is now {user_data['health']}%.")


def handle_user_input(update: Update, context: CallbackContext):
    logger.debug(f"Handling user input: {update.message.text} with context: {context.user_data}")
    
    logger.debug(f"Received user input: {update.message.text}. Context data: {context.user_data}")
    
    if context.user_data.get('expecting') == 'drug_amount':
        drug_name = context.user_data.get('buying')
        try:
            amount_to_buy = int(update.message.text)
            process_drug_purchase(update, context, drug_name, amount_to_buy)
        except ValueError:
            update.message.reply_text("Invalid input. Please enter a number.")
        finally:
            context.user_data.pop('expecting', None)
            context.user_data.pop('buying', None)
            
    elif context.user_data.get('expecting') == 'healthpack_amount':
        pack_size = context.user_data.get('buying_healthpack')
        try:
            amount_to_buy = int(update.message.text)
            buy_health_pack(update, context, pack_size, amount_to_buy)
        except ValueError:
            update.message.reply_text("Invalid input. Please enter a number.")
        finally:
            context.user_data.pop('expecting', None)
            context.user_data.pop('buying_healthpack', None)

def save_user_data(user_data):
    """
    Save the provided user data.

    This function acts as a wrapper around the save_data function 
    from the update_user_data module to maintain consistency in how
    user data is saved across the application.

    Parameters:
    - user_data (dict): The user data to be saved.
    """
    update_user_data.save_data(user_data)


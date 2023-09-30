from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import datetime
from dat_manager import get_user_data, update_user_data
from shop import HEALTH_PACKS, BACKPACKS
from prices import get_current_prices, base_prices


events = [
    {"effect": "bonus_drugs", "message": "You found a stash of drugs!"},
    {"effect": "fine", "message": "You were raided by the police."},
    {"effect": "health_decrease", "message": "A rival cartel attacked you."},
    {"effect": "cash_bonus", "message": "An anonymous benefactor gave you cash."},
]


def ask_drug_to_buy(update, context):
    # Get user data from the data manager.
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    city = user_data["city"]

    # Check if user has checked prices today
    last_checked_date = user_data.get("last_checked_date")

    today = datetime.date.today()

    # If user has not checked today or has never checked
    if not last_checked_date or datetime.datetime.strptime(last_checked_date, '%Y-%m-%d').date() < today:
        current_prices = get_current_prices(city)
        user_data["current_prices"] = current_prices  # store the current prices in user data
        user_data["last_checked_date"] = today.strftime('%Y-%m-%d')  # update the timestamp
        update_user_data(user_id, user_data)  # store the updated data back

    else:
        # use the stored prices if user has already checked today
        current_prices = user_data.get("current_prices", {})

    # Rest of your function (fetching drug list and creating keyboard)
    drug_list = list(base_prices[city].keys())
    keyboard = [
        [InlineKeyboardButton(f"{drug.capitalize()} (${current_prices[drug]})", callback_data=f'buy_{drug}')]
        for drug in drug_list
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select a drug to buy:', reply_markup=reply_markup)


def handle_buy_callback(update, context):
    query = update.callback_query
    drug_name = query.data.split('_')[1]  # The format is 'buy_drugname'

    # Identify user's city
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    city = user_data["city"]

    # Get current drug prices in the user's city
    city_drug_prices = get_current_prices(city)
    drug_price = city_drug_prices.get(drug_name)

    # If the drug price is not found, answer with an error
    if drug_price is None:
        query.answer(text="Unknown drug.")
        return

    # Handling health pack (assuming this is another feature you have)
    if query.data.startswith('buy_healthpack_'):
        health_pack_type = query.data.split('_')[2]
        query.edit_message_text(text=f"{health_pack_type.capitalize()} health packs restore {HEALTH_PACKS[health_pack_type]['health_restore']}% health and cost ${HEALTH_PACKS[health_pack_type]['price']}. To buy, use /buyhealthpack {health_pack_type} <amount>.")
        return

    # Handling backpack (assuming this is another feature you have)
    if query.data.startswith('buy_backpack_'):
        backpack_type = query.data.split('_')[2]
        query.edit_message_text(text=f"{backpack_type.capitalize()} backpacks have a capacity of {BACKPACKS[backpack_type]['capacity']} and cost ${BACKPACKS[backpack_type]['price']}. To buy, use /buybackpack {backpack_type}.")
        return

    # Display the drug price
    query.edit_message_text(text=f"The current price of {drug_name.capitalize()} is ${drug_price}. Enter the amount you wish to buy using /confirmbuy {drug_name} <amount>.")

def ask_drug_to_sell(update, context):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data:
        update.message.reply_text("Error fetching your data. Try again later.")
        return

    city = user_data["city"]
    current_prices = get_current_prices(city)  # Fetch current prices for the city

    # List only valid drugs that the user has in inventory
    drugs_to_list = [(drug, amount) for drug, amount in user_data["inventory"].items() if amount > 0 and drug in current_prices]

    # Update the keyboard buttons to include the current selling price for each drug
    keyboard = [[InlineKeyboardButton(f"💊 {drug.capitalize()} 📊({amount} units) 💲({current_prices[drug]} each)", callback_data=f'sell_{drug}')] for drug, amount in drugs_to_list]

    if not keyboard:
        update.message.reply_text("You have no drugs to sell.")
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("💼 Here's your drug stash with current selling prices. Select a drug to sell:", reply_markup=reply_markup)



def handle_sell_callback(update, context):
    query = update.callback_query
    drug_name = query.data.split('_')[1]  # The format is 'sell_drugname'

    user_id = update.effective_user.id
    user_data = get_user_data(user_id)

    if not user_data:
        query.answer(text="Error fetching your data. Try again later.")
        return

    city = user_data["city"]
    current_prices = get_current_prices(city)

    drug_price = current_prices.get(drug_name)

    if drug_price is None:
        query.answer(text="Unknown drug.")
        return

    # Since we're only getting one price now, we'll display that single price
    query.edit_message_text(text=f"You can sell {drug_name.capitalize()} for ${drug_price}. Enter the amount you wish to sell using /confirmsell {drug_name} <amount>.")

def confirm_buy(update, context):
    user_input = context.args
    
    # Minimum required input: type and item name or size
    if len(user_input) < 2:
        update.message.reply_text("Invalid format. Example usage: /confirmbuy drug <drug_name> <amount>.")
        return
    
    if user_input[0].lower() == "confirmbuy":
        user_input = user_input[1:]

    item_type = user_input[0].lower()

    
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)

    if item_type == "drug":
        print("Processing drug purchase...")  # Debugging line
        
        if len(user_input) != 3 or not user_input[2].isdigit():
            update.message.reply_text("Invalid format for drug. Usage: /confirmbuy drug <drug_name> <amount>.")
            return

        drug_name, amount = user_input[1], int(user_input[2])
        city = user_data["city"]
        city_drug_prices = get_current_prices(city)
        
        print(f"Drug name: {drug_name}, Amount: {amount}, City: {city}, City drug prices: {city_drug_prices}")  # Debugging line
        
        
        drug_name = drug_name.lower()
        
        allowed_drug_names = set()
        for city_drugs in base_prices.values():  # Iterating over drug dictionaries for each city
            for drug in city_drugs:
                allowed_drug_names.add(drug)
        
        
        if drug_name not in allowed_drug_names:
            update.message.reply_text(f"Unknown drug name: {drug_name}. Please choose a valid drug.")
            return


        drug_price = city_drug_prices.get(drug_name)

        
        if not drug_price:
            print(f"Drug {drug_name} not found in city {city}.")  # Debugging line
            update.message.reply_text("Unknown drug.")
            return
        
        # Check for negative or zero quantity
        if amount <= 0:
            update.message.reply_text("You can't buy a negative or zero quantity.")
            return

        price = drug_price

        total_price = price * amount

        # Validate that the user can afford the drugs and has space in their inventory
        if user_data["cash"] < total_price:
            update.message.reply_text("You don't have enough money.")
            return

        if sum(user_data["inventory"].values()) + amount > user_data["backpack_capacity"]:
            update.message.reply_text("You don't have enough space in your backpack.")
            return

        # Process transaction for drugs
        user_data["cash"] -= total_price
        user_data["inventory"][drug_name] = user_data["inventory"].get(drug_name, 0) + amount
        update_user_data(user_id, user_data)

        update.message.reply_text(f"Successfully bought {amount} {drug_name} for ${total_price}. You now have ${user_data['cash']}$.")
        event_message = random_event(user_id)
        update.message.reply_text(event_message)

    elif item_type == "backpack":
        backpack_type = user_input[1].lower()
        if backpack_type not in BACKPACKS:
            update.message.reply_text("Unknown backpack type.")
            return

        backpack_cost = BACKPACKS[backpack_type]["price"]
        backpack_capacity = BACKPACKS[backpack_type]["capacity"]

        # Check if user can afford the backpack
        if user_data["cash"] < backpack_cost:
            update.message.reply_text(f"You don't have enough money to buy a {backpack_type} backpack.")
            return

        # Check if user's current inventory can fit into the new backpack if it's smaller
        if sum(user_data["inventory"].values()) > backpack_capacity:
            update.message.reply_text(f"Your current inventory can't fit into a {backpack_type} backpack. You might need to sell some items first.")
            return

        # Deduct money and update backpack details
        user_data["cash"] -= backpack_cost
        user_data["backpack_capacity"] = backpack_capacity
        user_data["backpack_type"] = backpack_type  # You can track the type if you want
        update_user_data(user_id, user_data)

        update.message.reply_text(f"Successfully bought a {backpack_type} backpack for ${backpack_cost}. Your backpack can now hold {backpack_capacity} items.")


    elif item_type == "healthpack":
        if len(user_input) != 3 or not user_input[2].isdigit():
            update.message.reply_text("Invalid format for healthpack. Usage: /confirmbuy healthpack <size> <amount>.")
            return

        size, amount = user_input[1], int(user_input[2])
        total_cost = amount * HEALTH_PACKS[size]["price"]

        if user_data["cash"] < total_cost:
            update.message.reply_text(f"You don't have enough money to buy {amount} {size} health packs.")
            return

        # Deduct money and restore health
        user_data["cash"] -= total_cost
        user_data["health"] = min(100, user_data["health"] + amount * HEALTH_PACKS[size]["health_restore"])
        update_user_data(user_id, user_data)

        update.message.reply_text(f"Successfully bought {amount} {size} health packs for ${total_cost}. Your health is now {user_data['health']}%.")
    
    else:
        update.message.reply_text("Unknown item type.")

    
def random_event(user_id):
    """Trigger a random event for the user."""
    user_data = get_user_data(user_id)
    selected_event = random.choice(events)
    
    # Handle the effect of the event
    if selected_event["effect"] == "bonus_drugs":
        available_drugs = [drug for drug, amount in user_data["inventory"].items() if amount > 0]
        
        # If there are no drugs, return a default message
        if not available_drugs:
            return "You found a stash, but it was empty."
        
        drug = random.choice(available_drugs)
        quantity = random.randint(1, 10)  # Random quantity between 1 and 10
        user_data["inventory"][drug] = user_data["inventory"].get(drug, 0) + quantity
        selected_event["message"] = f"You found a stash of {drug}! Added {quantity} units to your inventory."

    elif selected_event["effect"] == "fine":
        fine_amount = random.randint(50, 200)  # Random fine between 50 and 200
        user_data["cash"] -= fine_amount
        selected_event["message"] = f"You were raided by the police and paid a fine of {fine_amount}$."

    elif selected_event["effect"] == "health_decrease":
        health_loss = random.randint(5, 20)  # Lose between 5% to 20% of health
        user_data["health"] -= health_loss
        selected_event["message"] = f"A rival cartel attacked you. You lost {health_loss}% health."

    elif selected_event["effect"] == "cash_bonus":
        bonus_amount = random.randint(100, 500)  # Bonus between 100 and 500
        user_data["cash"] += bonus_amount
        selected_event["message"] = f"An anonymous benefactor gave you {bonus_amount}$."

    # Remember to update the user data after making changes
    update_user_data(user_id, user_data)

    return selected_event["message"]


def confirm_sell(update, context):
    user_input = context.args
    
    if len(user_input) != 2 or not user_input[1].isdigit():
        update.message.reply_text("Invalid format. Please use /confirmsell <drug> <amount>.")
        return

    drug_name, amount = user_input[0], int(user_input[1])
    
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    city = user_data["city"]

    # Fetch current fluctuated prices for the user's city
    current_prices = get_current_prices(city)
    
    # Check if drug exists in current prices
    if drug_name not in current_prices:
        update.message.reply_text("Unknown drug.")
        return
    
     # Check for negative quantity
    if amount <= 0:
        update.message.reply_text("You can't sell a negative or zero quantity.")
        return

    price = current_prices[drug_name]
    total_price = price * amount

    # Validate that the user has the drugs to sell
    if user_data["inventory"].get(drug_name, 0) < amount:
        update.message.reply_text(f"You don't have {amount} {drug_name} to sell.")
        return

    # Process transaction
    user_data["cash"] += total_price
    user_data["inventory"][drug_name] -= amount
    if user_data["inventory"][drug_name] <= 0:
        del user_data["inventory"][drug_name]  # Remove the drug entry if there's none left
    update_user_data(user_id, user_data)

    update.message.reply_text(f"Successfully sold {amount} {drug_name} for ${total_price}. You now have ${user_data['cash']}$.")
    event_message = random_event(user_id)
    update.message.reply_text(event_message)
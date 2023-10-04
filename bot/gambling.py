from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dat_manager import get_user_data, update_user_data
import random

def start_gamble(update: Update, _):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    current_cash = user_data["cash"]

    # Check if user has enough cash to gamble
    if current_cash <= 0:
        update.message.reply_text("You don't have enough cash to gamble!")
        return
    
    # Generate a random drug-related scenario for gambling
    scenarios = [
        "You've heard rumors that a rival cartel is planning to transport a large shipment of drugs tonight. You want to bet on the outcome of the deal.",
        "There's a high-stakes poker game happening in the underground casino, and drug lords from all over the city are participating. Will you bet on the winning hand?",
        "A mysterious informant has given you insider information about a secret drug lab location. You're considering placing a bet on whether the police will raid the lab or not."
    ]
    selected_scenario = random.choice(scenarios)

    # Calculate maximum bet based on cash and daily limit
    max_bet = min(current_cash, user_data["daily_betting_limit"])

    # Create a gamble button for different amounts
    keyboard = [
        [InlineKeyboardButton(f"Bet $50 (Max: ${max_bet})", callback_data='gamble_50'),
         InlineKeyboardButton(f"Bet $100 (Max: ${max_bet})", callback_data='gamble_100')],
        [InlineKeyboardButton(f"Bet $500 (Max: ${max_bet})", callback_data='gamble_500')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"💼 : {selected_scenario}\n\n"
                              "Choose the amount you want to gamble:", reply_markup=reply_markup)
    
    
def gamble_callback(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    # Calculate maximum bet based on cash and daily limit
    max_bet = min(user_data["cash"], user_data["daily_betting_limit"])

    bet = int(query.data.split('_')[1])

    # Check if user exceeds maximum bet
    if bet > max_bet:
        query.edit_message_text(f"💸 You can't bet more than your current cash. Your maximum bet is ${max_bet}.")
        return

    # Check if user has enough cash
    if user_data["cash"] < bet:
        query.edit_message_text("You don't have enough cash!")
        return

    # Let's give a 50-50 chance for the user to win or lose
    if random.choice([True, False]):
        user_data["cash"] += bet
        user_data["gambling_wins"] += 1
        user_data["gambling_streak"] += 1
        if user_data["gambling_streak"] > user_data["max_gambling_streak"]:
            user_data["max_gambling_streak"] = user_data["gambling_streak"]
        query.edit_message_text(f"💰 You successfully predicted the outcome of the drug deal and earned ${bet}! "
                                f"Now you have ${user_data['cash']}.\n"
                                f"Current Gambling Streak: {user_data['gambling_streak']} 😎")
    else:
        user_data["cash"] -= bet
        user_data["gambling_losses"] += 1
        user_data["gambling_streak"] = 0
        query.edit_message_text(f"🚓 The police busted the drug deal, and you lost ${bet}. "
                                f"Now you have ${user_data['cash']}.\n"
                                f"Current Gambling Streak: {user_data['gambling_streak']} 🥺")

    # Update daily betting limit
    user_data["daily_betting_limit"] -= bet

    # Check if daily limit is reached
    if user_data["daily_betting_limit"] <= 0:
        query.message.reply_text("⏰ You've reached your daily betting limit. Come back tomorrow!")

    update_user_data(user_id, user_data)
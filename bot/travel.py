from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from dat_manager import get_user_data, update_user_data, initialize_user
import random
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Cities available for travel. You can expand this as required.
cities = ["Los Angeles", "New York", "Miami", "Chicago", "Houston"]

travel_cost_ranges = {
    "Los Angeles": (50, 120),   # Cost to travel to Los Angeles will be a random value between 80 and 120
    "New York": (100, 170),    # ... and so on for other cities
    "Miami": (40, 150),
    "Chicago": (45, 140),
    "Houston": (60, 130)
}

random_events = [
    {"description": "You were robbed during your journey!", "cash": -50, "health": -10},
    {"description": "You found a bag of money on the road!", "cash": 70},
    {"description": "You helped someone and got a reward!", "cash": 30},
    {"description": "You got into a fight and lost some health.", "health": -20},
    {"description": "You met a doctor who healed you.", "health": 20}
]

def end_game(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    

    score = user_data["cash"]  # You can modify this based on your game's scoring mechanism.
    

    update.message.reply_text(f"Game over! You played for 30 days and your final score is: ${score}. Your score has been added to the leaderboard.")

def restart_game(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # You can have some initialization logic for restarting here. 
    # For example, you can reset the user's data:
    initialize_user(user_id, update.message.from_user.first_name)

    restart_message = "The game has been restarted! Start fresh and make better choices this time!"
    update.message.reply_text(restart_message)


def list_cities(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    
    user_data["day"] = user_data.get("day", 0) + 1 
    current_day = user_data["day"]

    current_city = user_data['city']
    update_user_data(user_id, user_data)

    buttons = [
        [InlineKeyboardButton(city, callback_data=f'travel_{city}') for city in cities if city != current_city]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    update.message.reply_text("Choose a city to travel to:", reply_markup=reply_markup)
    
def travel_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    destination_city = query.data.split('_')[1]  # assuming data format is like 'travel_CityName'
    
    user_data = get_user_data(user_id)
    
    # Check for 30-day limit
    if user_data["day"] > 30:
        query.edit_message_text("You've reached the 30-day limit! Game over or provide further instructions here.")
        return
    
    # Check if the destination city is valid
    if destination_city not in travel_cost_ranges:
        logger.error(f"Invalid destination city {destination_city} for user {user_id}")

        query.edit_message_text(f"Error: {destination_city} is not a valid destination.")
        return

    
    # Deducting travel cost (randomly chosen from the defined range for the city)
    min_cost, max_cost = travel_cost_ranges[destination_city]
    travel_cost = random.randint(min_cost, max_cost)
    
    # Check if the user has enough money
    if user_data["cash"] < travel_cost:
        logger.warning(f"User {user_id} does not have enough money to travel to {destination_city}.")
        query.edit_message_text(f"You don't have enough money to travel to {destination_city}. It costs between ${min_cost} and ${max_cost}.")
        return

    user_data["city"] = destination_city
    user_data["cash"] -= travel_cost

    # Random event
    event = random.choice(random_events)
    user_data["cash"] += event.get("cash", 0)
    user_data["health"] += event.get("health", 0)
    
    # Check for health dropping to zero or below
    if user_data["health"] <= 0:
        user_data["health"] = 0
        query.edit_message_text(f"You have traveled to {destination_city} and spent ${travel_cost}. Unfortunately, your health has dropped to zero. Please seek medical help!")
        restart_game(update, context)
        update_user_data(user_id, user_data)
        return

    event_message = event["description"]

    # After factoring in the random event, if the user's cash is negative, revert the action
    if user_data["cash"] < 0:
        query.edit_message_text(f"You cannot afford to travel to {destination_city}. After considering potential costs and uncertainties during the journey, you would end up in debt!")
        return

    current_day = user_data["day"]
    
    # Save updated user data
    update_user_data(user_id, user_data)

    # Notify the user about their current status
    query.edit_message_text(
        f"📆 Day {current_day}: You have traveled to {destination_city} and spent ${travel_cost}.\n"
        f"{event_message}\n\n"
        f"Current Health: {user_data['health']}%\n"
        f"Current Cash: ${user_data['cash']}"
    )
    







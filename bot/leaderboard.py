from telegram import Update
from telegram.ext import CallbackContext
from dat_manager import users
import json

# Define a constant for maximum leaderboard entries (e.g., 10)
MAX_LEADERBOARD_ENTRIES = 10

def load_users_data():
    with open("../data/users.json", "r") as f:
        return json.load(f)

def get_top_players():
    """Return the top players based on cash."""
    users_data = load_users_data()
    return sorted(users_data.items(), key=lambda x: x[1]['cash'], reverse=True)[:MAX_LEADERBOARD_ENTRIES]

def format_leaderboard():
    """Format the leaderboard for display in the chat."""
    top_players = get_top_players()
    
    if not top_players:
        return "No entries on the leaderboard yet!"

    leaderboard_text = "🏆 Crypto Cartel Leaderboard 🏆\n\n"

    for rank, (user_id, data) in enumerate(top_players, 1):
        leaderboard_text += f"{rank}. User {user_id}: ${data['cash']}\n"

    return leaderboard_text

def leaderboard_command(update: Update, context: CallbackContext) -> None:
    all_users = users()
    # Sort users by cash
    sorted_users = sorted(all_users.values(), key=lambda x: x['cash'], reverse=True)
    
    leaderboard_text = "Leaderboard:\n"
    for idx, user_data in enumerate(sorted_users, 1):
        leaderboard_text += f"{idx}. {user_data['name']} - ${user_data['cash']}\n"

    update.message.reply_text(leaderboard_text)
    

def store_score_to_leaderboard(user_id, score):
    users_data = load_users_data()
    user_data = users_data.get(str(user_id), {})
    user_data["cash"] = score
    users_data[str(user_id)] = user_data

    # Save back to the JSON file
    with open("../data/users.json", "w") as f:
        json.dump(users_data, f)

    


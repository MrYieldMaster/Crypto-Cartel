import random
from datetime import datetime

users = {}  # This is a placeholder. In reality, you'd fetch from your database or JSON file.

def daily_bonus(user_id: int) -> str:
    """Give users daily bonuses."""
    current_date = datetime.now().date()

    # Check if user exists in the users dictionary, if not initialize them
    if user_id not in users:
        users[user_id] = {
            'cash': 0,
            'health': 100,  # or whatever default value you want
            'last_bonus_date': None,
            'streak': 0
        }

    if 'last_bonus_date' not in users[user_id] or users[user_id]['last_bonus_date'] != current_date:
        bonus_cash = random_bonus_amount(user_id)
        users[user_id]['cash'] += bonus_cash
        users[user_id]['last_bonus_date'] = current_date

        streak_message = handle_streaks(user_id)
        return f"🎁 Daily Bonus! 🎁\nYou received ${bonus_cash}. {streak_message}"

    return None


def random_bonus_amount(user_id: int) -> int:
    """Return a random bonus amount based on certain probabilities."""
    chances = random.randint(1, 100)

    if chances <= 70:  # 70% chance
        return random.randint(50, 100)
    elif 70 < chances <= 90:  # 20% chance
        return random.randint(101, 200)
    else:  # 10% chance
        return random.randint(201, 300)

def handle_streaks(user_id: int) -> str:
    """Manage and reward user for consecutive logins."""
    if 'streak' not in users[user_id]:
        users[user_id]['streak'] = 1
        return "It's your first day in a row! Keep it up!"
    
    if 'last_bonus_date' in users[user_id] and (datetime.now().date() - users[user_id]['last_bonus_date']).days == 1:
        users[user_id]['streak'] += 1
        streak_bonus = users[user_id]['streak'] * 10  # $10 for each day of the streak
        users[user_id]['cash'] += streak_bonus
        return f"🔥 {users[user_id]['streak']} day streak! 🔥 You received an extra ${streak_bonus}."
    
    users[user_id]['streak'] = 1  # Reset the streak if not consecutive
    return "Your streak was broken, but don't worry, keep playing!"

def random_daily_event(user_id: int) -> str:
    """Introduce random daily events that can have positive or negative impacts."""
    event_chance = random.randint(1, 100)

    if event_chance <= 10:  # 10% chance
        bonus_health = random.randint(1, 5)
        users[user_id]['health'] += bonus_health
        return f"🍏 Healthy Day! 🍏\nYou gained {bonus_health} health points."

    elif 10 < event_chance <= 20:  # 10% chance
        lost_cash = random.randint(1, 100)
        users[user_id]['cash'] -= lost_cash
        return f"💸 Bad Day! 💸\nYou lost ${lost_cash}."

    return None


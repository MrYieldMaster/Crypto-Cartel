import datetime
import logging
from telegram import Update
from telegram.ext import CallbackContext
from dat_manager import get_user_data, update_user_data, users

logging.basicConfig(level=logging.INFO)

LOAN_DURATION_DAYS = 7
INITIAL_INTEREST_RATE = 0.1
MAX_WARNINGS = 3  # Example number

def take_loan(user_id, amount):
    """Let the user take a loan."""
    
    # Error Handling for Negative Amounts
    if amount <= 0:
        logging.warning(f"User {user_id} attempted to take a loan of negative or zero amount: {amount}")
        return "Invalid amount. Please enter a positive value."

    user = get_user_data(user_id)

    # Refuse loans based on reputation
    if user["loan_reputation"] <= -2:
        return "Due to your loan history, we cannot offer you a loan at this time."

    if user["loan"] > 0:
        return "You already have an outstanding loan! Pay it back first."

    negotiation_bonus = 0
    if user["loan_reputation"] > 3:  # Good reputation
        negotiation_bonus = 0.02  # 2% reduction
    
    due_date = datetime.datetime.now() + datetime.timedelta(days=LOAN_DURATION_DAYS)
    user["loan_due_date"] = due_date
    interest = INITIAL_INTEREST_RATE - negotiation_bonus
    user["loan"] = amount * (1 + interest)
    user["cash"] += amount
    
    update_user_data(user_id, user)
    
    # ... [Rest of your code remains unchanged]

    logging.info(f"User {user_id} took a loan of {amount}$. Owing {user['loan']}$ by {user['loan_due_date'].strftime('%Y-%m-%d')}.")
    return (f"You've taken a loan of {amount}$. With an interest rate of {interest*100}%, "
            f"you owe us {user['loan']}$ by {user['loan_due_date'].strftime('%Y-%m-%d')}.")



def repay_loan(user_id, amount):
    """Let the user repay the loan."""

    if amount > user["cash"]:
        logging.warning(f"User {user_id} attempted to repay a loan with negative or zero amount: {amount}")
        return "You don't have enough cash to repay the loan."

    user = get_user_data(user_id)

    user["cash"] -= amount
    user["loan"] -= amount
    
    if amount <= 0:
        logging.warning(f"User {user_id} attempted to repay a loan with negative or zero amount: {amount}")
        return "Invalid amount. Please enter a positive value."


    # Check for overpayment
    if user["loan"] < 0:
        user["cash"] += abs(user["loan"])  # Refund overpayment
        user["loan"] = 0
        user["loan_reputation"] += 1
        user.pop("loan_due_date", None)
        user.pop("loan_warnings", None)
        return "You've repaid more than you owe! The excess amount has been refunded."

    logging.info(f"User {user_id} repaid {amount}$. Remaining loan amount: {user['loan']}$.")

    update_user_data(user_id, user)

    if user["loan"] == 0:
        user["loan_reputation"] += 1
        user.pop("loan_due_date", None)
        user.pop("loan_warnings", None)
        return "You've successfully repaid your loan. Good job!"
    else:
        return f"You still owe {user['loan']}$. Keep it up!"
    

def check_due_loans():
    """Check for due loans and apply penalties."""
    for user_id, user in users.items():
        if user.get("loan_due_date") and datetime.datetime.now() > user["loan_due_date"]:
            logging.info(f"Checking due loans for user {user_id}.")
            if "loan_warnings" not in user:
                user["loan_warnings"] = 0
            user["loan_warnings"] += 1

            if user["loan_warnings"] <= MAX_WARNINGS:
                penalty = INITIAL_INTEREST_RATE + (0.05 * user["loan_warnings"])  # Increase rate by 5% after each warning
                user["loan"] = user["loan"] * (1 + penalty)
                # Send warning message
                # For example, if you're using Telegram: 
                # context.bot.send_message(user_id, f"Warning {user['loan_warnings']}! Your loan is overdue. You now owe {user['loan']}$.")
            else:
                # Apply a heavy penalty or other game effect after max warnings
                user["cash"] -= user["loan"] * 0.5  # Take half of the loan amount from cash as a penalty
                user["loan_reputation"] -= 2
                user["loan"] = 0
                user.pop("loan_due_date", None)
                user.pop("loan_warnings", None)
                # context.bot.send_message(user_id, "Enforcers took half your cash! Better pay on time next time.")

# Make sure to periodically call `check_due_loans` in your game loop or as a scheduled job.

def take_loan_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        amount = int(context.args[0])
        message = take_loan(user_id, amount)
    except (IndexError, ValueError):
        message = "Usage: /take_loan <amount>"
    update.message.reply_text(message)

def repay_loan_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        amount = int(context.args[0])
        message = repay_loan(user_id, amount)
    except (IndexError, ValueError):
        message = "Usage: /repay_loan <amount>"
    update.message.reply_text(message)

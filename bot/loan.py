from datetime import datetime, timedelta
import logging
from telegram import Update
from telegram.ext import CallbackContext
from dat_manager import get_user_data, update_user_data, users, save_data, load_data

logging.basicConfig(level=logging.INFO)

LOAN_DURATION_DAYS = 7
INITIAL_INTEREST_RATE = 0.1
MAX_WARNINGS = 3  # Example number

def format_date_to_string(date_obj):
    try:
        return date_obj.strftime('%Y-%m-%d')
    except Exception as e:
        logging.error(f"Error formatting date: {e}")
        return "Error in Date"


def take_loan(user_id, amount):
    """Let the user take a loan."""
    
    # Error Handling for Negative Amounts
    if amount <= 0:
        logging.warning(f"User {user_id} attempted to take a loan of negative or zero amount: {amount}")
        return "Invalid amount. Please enter a positive value."

    user = get_user_data(user_id)
    logging.debug(f"User Data: {user}")

    # Initialize the loan_reputation key if it's missing
    if "loan_reputation" not in user:
        user["loan_reputation"] = 0

    # Refuse loans based on reputation
    if user.get("loan_reputation", 0) <= -2:
        return "Due to your loan history, we cannot offer you a loan at this time."

    if user["loan"] > 0:
        return "You already have an outstanding loan! Pay it back first."

    negotiation_bonus = 0
    if user.get("loan_reputation", 0) > 3:  # Good reputation
        negotiation_bonus = 0.02  # 2% reduction
        
    if user.get('loan_due_date'):
        formatted_date = user['loan_due_date'].strftime('%Y-%m-%d')
    else:
        formatted_date = "No Due Date Set"
        
    try:
        formatted_date = user['loan_due_date'].strftime('%Y-%m-%d')
    except Exception as e:
        logging.error(f"Error formatting date: {e}")
        formatted_date = "Error in Date"
        
    
    due_date = datetime.now() + timedelta(days=LOAN_DURATION_DAYS)
    user["loan_due_date"] = due_date.isoformat()
    interest = INITIAL_INTEREST_RATE - negotiation_bonus
    user["loan"] = amount * (1 + interest)
    user["cash"] += amount
    
    formatted_due_date = format_date_to_string(due_date)
    
    update_user_data(user_id, user)
    
    
    loan_due_date = datetime.fromisoformat(user['loan_due_date'])
    logging.info(f"User {user_id} took a loan of {amount}$. Owing {user['loan']}$ by {loan_due_date.strftime('%Y-%m-%d')}.")
    return (f"You've taken a loan of {amount}$. With an interest rate of {interest*100}%, "
            f"you owe us {user['loan']}$ by {formatted_due_date}.")
    
    
def take_loan_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        amount = int(context.args[0])
        message = take_loan(user_id, amount)
    except (IndexError, ValueError):
        message = "Usage: /take_loan <amount>"
    
    update.message.reply_text(message)
    
    


def repay_loan(user_id, amount):
    """Let the user repay the loan."""
    
    user = get_user_data(user_id)
    logging.debug(f"User Data: {user}")

    if amount > user["cash"]:
        logging.warning(f"User {user_id} attempted to repay a loan with insufficient funds: {amount}")
        return "You don't have enough cash to repay the loan."

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
                penalty = INITIAL_INTEREST_RATE + (0.05 * user["loan_warnings"])
                user["loan"] = user["loan"] * (1 + penalty)
                # Send warning message
            else:
                user["cash"] -= user["loan"] * 0.5
                user["loan_reputation"] -= 2
                user["loan"] = 0
                user.pop("loan_due_date", None)
                user.pop("loan_warnings", None)


def repay_loan_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        amount = int(context.args[0])
        message = repay_loan(user_id, amount)
    except (IndexError, ValueError):
        message = "Usage: /repay_loan <amount>"
    update.message.reply_text(message)
    

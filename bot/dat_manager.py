import json
import os


DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/users.json") 

USER_TEMPLATE = {
    "user_id": None,  # Unique identifier for the user
    "name": None,  # New field to store the user's name
    "cash": 1000,    # Starting cash amount, adjust as needed
    "health": 100,   # Percentage-based health, 100 being full health
    "inventory": {}, # Dictionary to store drug names as keys and amounts as values
    "backpack_capacity": 100, # Max number of drugs a user can carry, adjust as needed
    "city" : "Los Angeles", #set a default city for user
    "day" : 1,
    "loan": 0,  # Amount the user owes
    "loan_due_days": 0  # Days remaining to repay the loan (0 means no loan taken)
}

def initialize_user(user_id, user_name):
    """Ensure a user entry exists in the data."""
    data = load_data()
    if str(user_id) not in data:
        user_data = USER_TEMPLATE.copy()
        user_data["user_id"] = user_id
        user_data["name"] = user_name  # Store the user's name
        data[str(user_id)] = user_data
        print(f"Initialized data for user {user_id}: {user_data}")
        save_data(data)


def users():
    return load_data()


def load_data():
    """Load data from users.json."""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as file:
            try:
                with open(DATA_PATH, 'r') as file:
                   return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return {}
            except OSError as e:
                print(f"File I/O error: {e}")
                return {}



def save_data(data):
    """Save user data to the JSON file."""
    try:
        with open(DATA_PATH, 'w') as file:
             json.dump(data, file, indent=4)
    except OSError as e:
        print(f"File I/O error: {e}")
        
        
def get_user_data(user_id):
    """Fetch data for a specific user."""
    data = load_data()
    return data.get(str(user_id))

def update_user_data(user_id, user_data):
    """Update data for a specific user."""
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)
            

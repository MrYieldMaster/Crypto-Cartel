# Define drugs
DRUGS = {
    "weed": {
        "min_price": 10,
        "max_price": 50,
        "description": "Weed. Common and loved by many."
    },
    "cocaine": {
        "min_price": 20,
        "max_price": 100,
        "description": "Cocaine. Expensive and very profitable."
    },
    "meth": {
        "min_price": 5,
        "max_price": 70,
        "description": "Meth. Volatile prices, but can be very profitable."
    },
    "magic_mushrooms": {
        "min_price": 15,
        "max_price": 60,
        "description": "Magic Mushrooms. A psychedelic experience."
    }
}

# Define backpacks
BACKPACKS = {
    "small_backpack": {
        "capacity": 100,  # units
        "price": 50,  # in-game currency
        "description": "A small backpack. Can hold up to 100 units of drugs."
    },
    "medium_backpack": {
        "capacity": 250,
        "price": 200,
        "description": "A medium-sized backpack. Can hold up to 250 units of drugs."
    },
    "large_backpack": {
        "capacity": 500,
        "price": 500,
        "description": "A large backpack. Can hold up to 500 units of drugs."
    }
}

# Function to get drug details
def get_drug_details(drug_name):
    return DRUGS.get(drug_name, None)

# Function to get backpack details
def get_backpack_details(backpack_name):
    return BACKPACKS.get(backpack_name, None)

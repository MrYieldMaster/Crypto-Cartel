import random

# A dictionary of base prices for each drug in each city.
base_prices = {
    "Los Angeles": {"cocaine": 1000, "heroin": 1200, "weed": 300},
    "New York": {"cocaine": 1200, "heroin": 1000, "weed": 250},
    "Miami": {"cocaine": 900, "heroin": 1100, "weed": 320},
    "Chicago": {"cocaine": 1050, "heroin": 1150, "weed": 280},
    "Houston": {"cocaine": 1100, "heroin": 1080, "weed": 310}
}

fluctuation_rates = {
    "cocaine": (-20, 20),
    "heroin": (-15, 15),
    "weed": (-10, 10)
}

def get_current_prices(city):
    """Generate dynamic prices based on base prices.
    Args:
    - city (str): Name of the city to get prices for.

    Returns:
    - dict: Dictionary of fluctuated prices for each drug.
    """
    city_prices = base_prices.get(city)
    
    # If city is not found in base_prices
    if city_prices is None:
        print(f"Prices for city '{city}' not found!")
        return {}

    fluctuated_prices = {}
    for drug, price in city_prices.items():
        min_fluct, max_fluct = fluctuation_rates.get(drug, (-20, 20))
        fluctuation = random.randint(min_fluct, max_fluct) / 100
        fluctuated_price = price + (price * fluctuation)
        fluctuated_prices[drug] = round(fluctuated_price)

    return fluctuated_prices

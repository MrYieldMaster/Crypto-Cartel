import pygame
from pygame.locals import QUIT
import asyncio
import aiofiles
import json
from prices import get_current_prices
from dat_manager import get_user_data
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/users.json")
CURRENT_USER_PATH = os.path.join(os.path.dirname(__file__), "../data/current_user.txt")

DEFAULT_USER = get_user_data

current_user_data = None
current_drug_prices = None

async def update_data():
    global current_user_data, current_drug_prices
    while True:
        try:
            async with aiofiles.open(DATA_PATH, "r") as file:
                data = await file.read()
                users_data = json.loads(data)
                if users_data:
                    # Fetch the data for the first user by ID, assuming user IDs are sorted
                    first_user_id = list(users_data.keys())[0]
                    current_user_data = users_data[first_user_id]
                    current_city = current_user_data["city"]
                    current_drug_prices = get_current_prices(current_city)
        except (FileNotFoundError, json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"Error in update_data: {e}")
        await asyncio.sleep(5)



async def fetch_current_user():
    try:
        async with aiofiles.open(CURRENT_USER_PATH, mode="r") as f:
            user_data = await f.read()
            stripped_data = user_data.strip()
            if not stripped_data:
                print("User data file is empty. Setting to default user.")
                return DEFAULT_USER
            return int(stripped_data)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error in fetch_current_user: {e}")
        return 0



async def game_loop(screen, clock):
    global current_user_data, current_drug_prices
    running = True
    user_id = 0
    font = pygame.font.SysFont(None, 25)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        screen.fill((255, 255, 255))

        new_user_id = await fetch_current_user()
        if new_user_id != user_id:
            user_id = new_user_id
            user_data = get_user_data(user_id)
            if user_data:
                current_user_data = user_data

        if current_user_data:
            user_text = font.render(f"User: {current_user_data['name']}, City: {current_user_data['city']}", True, (0, 0, 0))
            screen.blit(user_text, (20, 20))
        
        if current_drug_prices:
            y_offset = 60
            for drug, price in current_drug_prices.items():
                drug_text = font.render(f"{drug}: ${price}", True, (0, 0, 0))
                screen.blit(drug_text, (20, y_offset))
                y_offset += 30

       
        pygame.display.flip()
        await asyncio.sleep(1/60)

def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Crypto Cartel")

    clock = pygame.time.Clock()

    loop = asyncio.get_event_loop()
    loop.create_task(update_data())
    loop.run_until_complete(game_loop(screen, clock))

    pygame.quit()

if __name__ == "__main__":
    main()

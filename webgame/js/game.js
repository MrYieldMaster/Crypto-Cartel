document.addEventListener('DOMContentLoaded', function() {
    // Initialize game state and load data, perhaps from the data you've shared.
    // Add game logic here.
})


// Player Data (Using the sample user data structure)
const player = {
    id: "sample_user_id",
    name: "Sample User",
    cash: 1000,
    health: 100,
    inventory: [],
    city: "New York",
    day: 1,
    loan: {},
    gambling: {},
    score: 0
}

// Backpacks & Health Packs (From shop.py)
const BACKPACKS = {
    // ... (Based on shop.py content)
}

const HEALTH_PACKS = {
    // ... (Based on shop.py content)
}

// Base Prices & Fluctuation Rates (From prices.py)
const base_prices = {
    // ... (Based on prices.py content)
}

const fluctuation_rates = {
    // ... (Based on prices.py content)
}

// Dynamic Pricing Function (Adapting the get_current_prices function)
function getCurrentPrices(city) {
    // ... (Adapted logic from prices.py)
}

// Function to initialize the game state
function initializeGame() {
    // Populate player stats, marketplace, inventory, etc.
    // ... (Based on the earlier provided logic)
}

// Initialize the game when the document is ready
document.addEventListener('DOMContentLoaded', initializeGame);

// Function to buy a drug
function buyDrug(drugName, quantity) {

    let drugPrice = getCurrentPrices(player.city)[drugName];
    let totalCost = drugPrice * quantity;


    // Check if the player has enough money
    if (player.cash >= totalCost) {
        player.cash -= totalCost;

        // Add the drug to the player's inventory or update the quantity
        let drugInInventory = player.inventory.find(item => item.name === drugName);
        if (drugInInventory) {
            drugInInventory.units += quantity;
            if (isNaN(quantity) || quantity <= 0) {
                alert("Please enter a valid quantity!");
                return;
        } else {
            player.inventory.push({name: drugName, units: quantity});
        }

        updatePlayerStats();
    } else {
        alert("You don't have enough money!");
    }
}

// Function to sell a drug
function sellDrug(drugName, quantity) {
    let drugInInventory = player.inventory.find(item => item.name === drugName);

    // Check if the player has the drug in the inventory and enough quantity
    if (drugInInventory && drugInInventory.units >= quantity) {
        let drugPrice = getCurrentPrices(player.city)[drugName];
        let totalRevenue = drugPrice * quantity;

        player.cash += totalRevenue;
        drugInInventory.units -= quantity;

        

        // Remove the drug from inventory if quantity is zero
        if (isNaN(quantity) || quantity <= 0) {
            alert("Please enter a valid quantity!");
            return;
        } else if (drugInInventory.units === 0) {
            player.inventory = player.inventory.filter(item => item.name !== drugName);
        }
        

        updatePlayerStats();
    } else {
        alert("You don't have enough of the selected drug to sell!");
    }
}

// Function to update the player's displayed stats
function updatePlayerStats() {
    // ... (Update the displayed stats using the player object data)
}

function shareScore(score) {
    // Use Telegram's shareGameScore method
    TelegramGameProxy.shareScore(score);
}

function getHighScores() {
    // Use Telegram's getHighScores method
    TelegramGameProxy.getHighScores();
}

function setGameScore(score, force) {
    // Use Telegram's setGameScore method
    TelegramGameProxy.setGameScore(score, force);
}

function getGameHighScores() {
    // Use Telegram's getGameHighScores method
    TelegramGameProxy.getGameHighScores();
}

function getGameScore() {
    // Use Telegram's getGameScore method
    TelegramGameProxy.getGameScore();
}

// Attach event handlers to Buy/Sell buttons for each drug in the marketplace
document.getElementById('drugList').addEventListener('click', function(event) {
    if (event.target.tagName === 'BUTTON') {
        let drugName = event.target.parentElement.firstChild.nodeValue.split(":")[0].trim();
        let action = event.target.innerText;
        let quantity = parseInt(prompt("Enter the quantity you wish to " + action.toLowerCase() + ":", "1"));

        if (!isNaN(quantity) && quantity > 0) {
            if (action === "Buy") {
                buyDrug(drugName, quantity);
            } else if (action === "Sell") {
                sellDrug(drugName, quantity);
            }
        } else {
            alert("Please enter a valid quantity!");
        }
    }
})

// List of cities (For simplicity, using a static list. Can be derived dynamically from base_prices)
const cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"];

// Function for traveling to a new city
function travel() {
    let citySelection = prompt("Select a city to travel to:\\n" + cities.join("\\n"));
    
    if (cities.includes(citySelection)) {
        if (!cities.includes(citySelection)) {
            alert("Invalid city selection. Please choose a valid city!");
            return;
        }

        player.city = citySelection;

    // Introducing random travel events
    let randomEvent = Math.floor(Math.random() * 5);
    switch (randomEvent) {
        case 0:
            alert("You've been robbed! Lost half your money.");
            player.cash /= 2;
            break;
        case 1:
            alert("You found a hidden stash of drugs. Sold them for extra cash!");
            player.cash += 500;  // This can be a random value or based on player's current status
            break;
        case 2:
            alert("You've been caught by the police and had to pay a fine.");
            player.cash -= 300;  // This can be a random value or based on player's current status
            break;
        // More random events can be added
    }
        
        // Update marketplace prices based on the new city
    updateMarketplacePrices();

        updatePlayerStats();
    } else {
        alert("Invalid city selection. Please choose a valid city!");
    }
}

// Attach event handler to the Travel button
document.getElementById('travelBtn').addEventListener('click', travel);

// Function to update the displayed drug prices based on the current city
function updateMarketplacePrices() {
    let currentPrices = getCurrentPrices(player.city);
    let drugs = document.getElementById('drugList').children;
    
    for (let i = 0; i < drugs.length; i++) {
        let drugName = drugs[i].firstChild.nodeValue.split(":")[0].trim();
        drugs[i].firstChild.nodeValue = drugName + ": $" + currentPrices[drugName];
    }
}

// Function to update the player's displayed stats
function updatePlayerStats() {
    document.getElementById('playerMoney').innerText = "Money: $" + player.cash;
    document.getElementById('playerHealth').innerText = "Health: " + player.health + "%";
    document.getElementById('gameDay').innerText = "Day: " + player.day + "/30";
    document.getElementById('playerCity').innerText = "City: " + player.city;

    // Update player's inventory display
    let ownedDrugs = document.getElementById('ownedDrugs');
    ownedDrugs.innerHTML = '';  // Clear current inventory display
    player.inventory.forEach(drug => {
        let drugElement = document.createElement('div');
        drugElement.className = 'drug';
        drugElement.innerText = drug.name + ": " + drug.units + " units";
        ownedDrugs.appendChild(drugElement);
    });

    // Update the marketplace drug prices
    updateMarketplacePrices();
}

// Loan data structure
const loan = {
    amount: 0,  // Amount borrowed
    dueDate: 0,  // Day by which the loan should be repaid
    interestRate: 0.1  // 10% interest rate (can be adjusted)
}

// Function to take a loan
function takeLoan(amount) {
    if (loan.amount > 0) {
        alert("You already have an outstanding loan!");
        return;
    }

    loan.amount = amount;
    loan.dueDate = player.day + 5;  // Loan should be repaid in 5 days (can be adjusted)
    player.cash += amount;

    alert("You've taken a loan of $" + amount + ". Repay by day " + loan.dueDate + " to avoid penalties!");
    updatePlayerStats();
}

// Function to repay the loan
function repayLoan(amount) {
    if (loan.amount === 0) {
        alert("You don't have an outstanding loan!");
        return;
    }

    let repaymentAmount = loan.amount * (1 + loan.interestRate);
    if (player.cash < repaymentAmount) {
        alert("You don't have enough money to repay the loan!");
        return;
    }

    player.cash -= repaymentAmount;
    loan.amount = 0;
    loan.dueDate = 0;

    alert("Loan repaid successfully!");
    updatePlayerStats();
}

// Function to check loan status and apply penalties if not repaid on time
function checkLoanStatus() {
    if (loan.amount > 0 && player.day > loan.dueDate) {
        alert("You failed to repay your loan on time! Facing penalties.");
        
        // Apply penalties (can be adjusted)
        player.cash -= loan.amount;  // Deduct the loan amount from player's cash
        player.health -= 10;  // Deduct 10% health
        if (player.health <= 0) {
            // Player loses the game
            gameOver();
        }

        // Clear the loan data
        loan.amount = 0;
        loan.dueDate = 0;

        updatePlayerStats();
    }
}

// Function to handle game over scenario
function gameOver() {
    alert("Game Over! You've lost.");
    // Reset game state or navigate to a game over screen
}

// Sample feedback messages for different game actions
const feedbackMessages = {
    loanTaken: "You've taken a loan. Make sure to repay by the due date!",
    loanRepaySuccess: "You've successfully repaid your loan.",
    loanRepayFail: "You failed to repay your loan on time! Facing penalties.",
    boughtDrug: "Drug purchased successfully!",
    soldDrug: "Drug sold successfully!",
    invalidAction: "Invalid action. Please try again.",
    travelSuccess: "You've traveled to a new city!"
    // ... Add more feedback messages as needed
}

// Function to show feedback messages
function showFeedbackMessage(messageKey) {
    if (feedbackMessages[messageKey]) {
        alert(feedbackMessages[messageKey]);
    }
}


// Adding tooltips for game elements (Sample for drugs)
const drugTooltips = {
    // Sample tooltips for drugs. This can be expanded based on game data.
    "Cocaine": "A powerful stimulant. High demand in some cities.",
    "Weed": "Commonly used recreational drug. Prices may vary."
    // ... Add tooltips for other drugs or game elements
}

// Function to show tooltips
function showTooltip(element) {
    let tooltipText = drugTooltips[element.innerText.split(":")[0].trim()];
    if (tooltipText) {
        // Display the tooltip. This is a simple example and can be enhanced using CSS or other frontend frameworks.
        element.setAttribute("title", tooltipText);
    }
}

// Simple animation for traveling (Using CSS transitions)
// Assuming there's a CSS class called 'travelAnimation' that handles the animation
function buyDrug(drugName, quantity) {

    let drugPrice = getCurrentPrices(player.city)[drugName];
    let totalCost = drugPrice * quantity;


    // Check if the player has enough money
    if (player.cash >= totalCost) {
        player.cash -= totalCost;

        // Add the drug to the player's inventory or update the quantity
        let drugInInventory = player.inventory.find(item => item.name === drugName);
        if (drugInInventory) {
            drugInInventory.units += quantity;
        } else {
            player.inventory.push({name: drugName, units: quantity});
        }

        if (isNaN(quantity) || quantity <= 0) {
            alert("Please enter a valid quantity!");
            return;
        }

        updatePlayerStats();
    } else {
        alert("You don't have enough money!");
    }
}

// Rival Drug Lords
const rivalLords = [
    {name: "Don Vito", strength: 10, bribeAmount: 500},
    {name: "El Chapo", strength: 15, bribeAmount: 700},
    {name: "Pablo", strength: 20, bribeAmount: 1000},
    // ... Add more rivals as needed
]

function encounterRival() {
    let rival = rivalLords[Math.floor(Math.random() * rivalLords.length)];
    let action = prompt(`You've encountered ${rival.name}! Choose an action:\\n1. Pay off ($${rival.bribeAmount})\\n2. Fight\\n3. Form alliance (costs 50% of current cash)`);

    switch (action) {
        case "1":  // Pay off
            if (player.cash >= rival.bribeAmount) {
                player.cash -= rival.bribeAmount;
                showFeedbackMessage("Paid off the rival successfully!");
            } else {
                showFeedbackMessage("Not enough cash to pay off!");
            }
            break;
        case "2":  // Fight
            if (Math.random() * 20 > rival.strength) {
                showFeedbackMessage(`You defeated ${rival.name} and gained some cash!`);
                player.cash += rival.bribeAmount;
            } else {
                showFeedbackMessage(`You were defeated by ${rival.name} and lost some cash!`);
                player.cash -= rival.bribeAmount;
                player.health -= 10;  // Lose some health
            }
            break;
        case "3":  // Form alliance
            if (player.cash >= player.cash / 2) {
                player.cash /= 2;
                // Set alliance flag (this can be used to modify game behavior while in alliance)
                player.inAlliance = true;
                showFeedbackMessage(`Formed an alliance with ${rival.name}!`);
            } else {
                showFeedbackMessage("Not enough cash to form an alliance!");
            }
            break;
        default:
            showFeedbackMessage("Invalid action chosen!");
            break;
    }

    updatePlayerStats();
}

// Special Missions
const missions = [
    {name: "Smuggle drugs", reward: 1000, risk: 10},
    {name: "Broker peace deal", reward: 1500, risk: 5},
    {name: "Evade police", reward: 500, risk: 15},
    // ... Add more missions as needed
]


function offerMission() {
    let mission = missions[Math.floor(Math.random() * missions.length)];
    let accept = confirm(`Special Mission: ${mission.name}\\nReward: $${mission.reward}\\nDo you accept?`);

    if (accept) {
        if (Math.random() * 100 < mission.risk) {
            showFeedbackMessage(`Mission failed! You lost some cash.`);
            player.cash -= mission.reward / 2;
            player.health -= 10;  // Lose some health
        } else {
            showFeedbackMessage(`Mission successful! You gained $${mission.reward}.`);
            player.cash += mission.reward;
        }

        updatePlayerStats();
    } else {
        showFeedbackMessage("Mission declined.");
    }
}

// Save game state
localStorage.setItem('playerData', JSON.stringify(player));

// Retrieve game state
let savedData = localStorage.getItem('playerData');
if (savedData) {
    player = JSON.parse(savedData);
}


// Function to share player's score
function sharePlayerScore() {
    TelegramGameProxy.shareScore(player.score);
}

// Function to view leaderboard (for demonstration; actual implementation might be more complex)
function viewLeaderboard() {
    let leaderboard = TelegramGameProxy.getGameHighScores();
    // Display the leaderboard in a dedicated section or modal
    // This is a basic example; actual implementation can vary based on how you wish to display it
    let leaderboardSection = document.getElementById('leaderboardSection');
    leaderboardSection.innerHTML = '';
    leaderboard.forEach(entry => {
        leaderboardSection.innerHTML += `<p>${entry.user.first_name}: ${entry.score}</p>`;
    });
}

// Attach event handlers
document.getElementById('shareScoreBtn').addEventListener('click', sharePlayerScore);
document.getElementById('viewLeaderboardBtn').addEventListener('click', viewLeaderboard);



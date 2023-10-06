

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
};

const BACKPACKS = {};
const HEALTH_PACKS = {};
const base_prices = {};
const fluctuation_rates = {};

const cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"];
const feedbackMessages = {
    loanTaken: "You've taken a loan. Make sure to repay by the due date!",
    loanRepaySuccess: "You've successfully repaid your loan.",
    loanRepayFail: "You failed to repay your loan on time! Facing penalties.",
    boughtDrug: "Drug purchased successfully!",
    soldDrug: "Drug sold successfully!",
    invalidAction: "Invalid action. Please try again.",
    travelSuccess: "You've traveled to a new city!"
};
const drugTooltips = {
    "Cocaine": "A powerful stimulant. High demand in some cities.",
    "Weed": "Commonly used recreational drug. Prices may vary."
};
const rivalLords = [
    {name: "Don Vito", strength: 10, bribeAmount: 500},
    {name: "El Chapo", strength: 15, bribeAmount: 700},
    {name: "Pablo", strength: 20, bribeAmount: 1000}
];
const missions = [
    {name: "Smuggle drugs", reward: 1000, risk: 10},
    {name: "Broker peace deal", reward: 1500, risk: 5},
    {name: "Evade police", reward: 500, risk: 15}
];
const loan = {
    amount: 0,
    dueDate: 0,
    interestRate: 0.1
};

// Functions

function getCurrentPrices(city) {
    // ... (Adapted logic from prices.py)
}

function initializeGame() {
    // ... (Based on the earlier provided logic)
}

function buyDrug(drugName, quantity) {
    if (isNaN(quantity) || quantity <= 0) {
        alert("Please enter a valid quantity!");
        return;
    }

    let drugPrice = getCurrentPrices(player.city)[drugName];
    let totalCost = drugPrice * quantity;

    if (player.cash >= totalCost) {
        player.cash -= totalCost;

        let drugInInventory = player.inventory.find(item => item.name === drugName);
        if (drugInInventory) {
            drugInInventory.units += quantity;
        } else {
            player.inventory.push({name: drugName, units: quantity});
        }

        updatePlayerStats();
    } else {
        alert("You don't have enough money!");
    }
}

function sellDrug(drugName, quantity) {
    if (isNaN(quantity) || quantity <= 0) {
        alert("Please enter a valid quantity!");
        return;
    }

    let drugInInventory = player.inventory.find(item => item.name === drugName);
    if (drugInInventory && drugInInventory.units >= quantity) {
        let drugPrice = getCurrentPrices(player.city)[drugName];
        let totalRevenue = drugPrice * quantity;

        player.cash += totalRevenue;
        drugInInventory.units -= quantity;

        if (drugInInventory.units === 0) {
            player.inventory = player.inventory.filter(item => item.name !== drugName);
        }

        updatePlayerStats();
    } else {
        alert("You don't have enough of the selected drug to sell!");
    }
}

function updateMarketplacePrices() {
    let drugList = document.getElementById('drugList');
    drugList.innerHTML = '';  // Clear current drug list

    let drugPrices = getCurrentPrices(player.city);
    for (let drugName in drugPrices) {
        let drugElement = document.createElement('div');
        drugElement.className = 'drug';
        drugElement.innerText = drugName + ": $" + drugPrices[drugName];
        drugElement.setAttribute('title', drugTooltips[drugName]);
        drugElement.setAttribute('onmouseover', 'showTooltip(this)');
        drugElement.setAttribute('onmouseout', 'hideTooltip(this)');

        let buyButton = document.createElement('button');
        buyButton.innerText = "Buy";
        buyButton.className = 'btn btn-primary';

        let sellButton = document.createElement('button');
        sellButton.innerText = "Sell";
        sellButton.className = 'btn btn-primary';

        drugElement.appendChild(buyButton);
        drugElement.appendChild(sellButton);

        drugList.appendChild(drugElement);
    }
}

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


function takeLoan(amount) {
    if (player.loan.amount > 0) {
        alert("You already have an outstanding loan!");
        return;
    }

    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount!");
        return;
    }

    player.loan.amount = amount;
    player.loan.dueDate = player.day + 30;
    player.cash += amount;
    player.score += amount;
    showFeedbackMessage('loanTaken');
}

function repayLoan(amount) {
    if (player.loan.amount <= 0) {
        alert("You don't have an outstanding loan!");
        return;
    }

    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount!");
        return;
    }

    if (amount > player.cash) {
        alert("You don't have enough cash to repay the loan!");
        return;
    }

    player.loan.amount -= amount;
    player.cash -= amount;
    player.score -= amount;
    showFeedbackMessage('loanRepaySuccess');
}


function checkLoanStatus() {
    if (player.loan.amount > 0) {
        if (player.day > player.loan.dueDate) {
            let interest = player.loan.amount * player.loan.interestRate;
            player.loan.amount += interest;
            player.cash -= interest;
            player.score -= interest;
            showFeedbackMessage('loanRepayFail');
        } else if (player.day === player.loan.dueDate) {
            player.loan.amount = 0;
            player.loan.dueDate = 0;
            showFeedbackMessage('loanRepaySuccess');
        }
    }

}

function gameOver() {
    if (player.health <= 0) {
        alert("You are dead!");
        TelegramGameProxy.setGameScore(player.score);
        TelegramGameProxy.setGameHighScore(player.score);
        TelegramGameProxy.setGameOver();
    }

    if (player.day > 30) {
        alert("You've run out of time!");
        TelegramGameProxy.setGameScore(player.score);
        TelegramGameProxy.setGameHighScore(player.score);
        TelegramGameProxy.setGameOver();
    }
}

function gamble(amount) {
    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount!");
        return;
    }

    if (amount > player.cash) {
        alert("You don't have enough cash to gamble!");
        return;
    }

    let winChance = Math.random();
    if (winChance > 0.5) {
        player.cash += amount;
        player.score += amount;
        showFeedbackMessage('gambleWin');
    } else {
        player.cash -= amount;
        player.score -= amount;
        showFeedbackMessage('gambleLose');
    }
}


function showFeedbackMessage(messageKey) {
    if (feedbackMessages[messageKey]) {
        alert(feedbackMessages[messageKey]);
    }
}

function showTooltip(element) {
    let tooltipText = drugTooltips[element.innerText.split(":")[0].trim()];
    if (tooltipText) {
        // Display the tooltip. This is a simple example and can be enhanced using CSS or other frontend frameworks.
        element.setAttribute("title", tooltipText);
    }
}

function drugTooltips (element) {
    element.setAttribute("title", "A powerful stimulant. High demand in some cities.");
}




function encounterRival() {
    // ... (Rival encounter logic)
}

function offerMission() {
    // ... (Mission offering logic)
}

// Event Listeners

document.addEventListener('DOMContentLoaded', initializeGame);

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
});

document.getElementById('travelBtn').addEventListener('click', travel);

document.getElementById('shareScoreBtn').addEventListener('click', function() {
    TelegramGameProxy.shareScore(player.score);
});

document.getElementById('viewLeaderboardBtn').addEventListener('click', function() {
    let leaderboard = TelegramGameProxy.getGameHighScores();
    let leaderboardSection = document.getElementById('leaderboardSection');
    leaderboardSection.innerHTML = '';
    leaderboard.forEach(entry => {
        leaderboardSection.innerHTML += `<p>${entry.user.first_name}: ${entry.score}</p>`;
    });
});

// Saving & Retrieving game state
localStorage.setItem('playerData', JSON.stringify(player));

let savedData = localStorage.getItem('playerData');
if (savedData) {
    player = JSON.parse(savedData);
}

from cs50 import get_float


while True:
    cents = get_float("Change owed: ")  # Ask user for how many
    if (cents > 0):
        break  # Stop asking cents owed

cents = round(cents * 100)

# Cet total coins to 0
coins = 0

# Calculate quarters
while cents >= 25:
    cents = cents - 25
    coins += 1

# Calculate dimes
while cents >= 10:
    cents = cents - 10
    coins += 1

# Calculate nickels
while cents >= 5:
    cents = cents - 5
    coins += 1

# Calculate pennies
while cents >= 1:
    cents = cents - 1
    coins += 1

# Print total number of coins
print(f"Total coins: {coins}")

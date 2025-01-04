#include <cs50.h>
#include <stdio.h>

int calculate_quarters(int cents);
int calculate_dimes(int cents);
int calculate_nickels(int cents);
int calculate_pennies(int cents);

int main(void)
{
    // Prompt user for change owed, in cents
    int cents;
    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);
    {
        // Calculate how many quarters you should give customer
        int quarters = calculate_quarters(cents);
        cents = cents - (quarters * 25);

        // Calculate how many dimes you should give customer
        int dimes = calculate_dimes(cents);
        cents = cents - (dimes * 10);

        // Calculate how many nickels you should give customer
        int nickels = calculate_nickels(cents);
        cents = cents - (nickels * 5);

        // Calculate how many pennies you should give customer
        int pennies = calculate_pennies(cents);
        cents = cents - (pennies * 1);

        // Sum of coins
        int coins = quarters + dimes + nickels + pennies;

        // Print total number of coins
        printf("%i\n", coins);
    }
}
int calculate_quarters(int cents)
{
    // First you start counting the quarters at 0
    // If the cents are more or equal to 25 cents
    int quarters = 0;
    while (cents >= 25)
    {
        // count 1 coin up and substract 25 coins from cents
        quarters++;
        cents = cents - 25;
    }
    return quarters;
}
int calculate_dimes(int cents)
{
    int dimes = 0;
    while (cents >= 10)
    {
        cents = cents - 10;
        dimes++;
    }
    return dimes;
}
int calculate_nickels(int cents)
{
    int nickels = 0;
    while (cents >= 5)
    {
        cents = cents - 5;
        nickels++;
    }
    return nickels;
}
int calculate_pennies(int cents)
{
    int pennies = 0;
    while (cents >= 1)
    {
        cents = cents - 1;
        pennies++;
    }
    return pennies;
}

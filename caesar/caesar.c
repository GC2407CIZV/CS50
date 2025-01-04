#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
    if (argc != 2) // if the key is not = to 2
    {
        printf("Usage: ./caesar key \n"); // Print error message and how use
        return 1;                         // Quit program
    }

    for (int i = 0; i < strlen(argv[1]); i++) // check char. if it's a digit
    {
        if (!isdigit(argv[1][i])) // if not a digit
        {
            printf("Usage: ./caesar key \n"); // Print error message and how use
            return 1;                         // Quit program
        }
    }
    int k = atoi(argv[1]);                        // Converts string number to int number (key)
    string plaintext = get_string("Plaintext: "); // Get string from user
    printf("Ciphertext: ");

    // Check the whole plaintext 1 character at the time
    for (int j = 0; j < strlen(plaintext); j++)
    {
        // if uppercase bring A to value 0 (65-65) + the key mod26 + 65
        // If the key is 1 to make the alfabet loop back use (text - 65 + key mod 26 + 65)
        // Z = 90 => Z = 90 - 65 => Z = 25 + 1 (key) => Z = 26 mod 26 (loops back to first letter)=>
        // Z=0 + 65 => Z = 65 = A
        if (isupper(plaintext[j])) // If uppercase
        {
            printf("%c", (plaintext[j] - 65 + k) % 26 + 65);
        }
        else if (islower(plaintext[j])) // If lowercase
        {
            printf("%c", (plaintext[j] - 97 + k) % 26 + 97);
        }
        else // If anything else (number, punctuation,..) don't change
        {
            printf("%c", plaintext[j]);
        }
    }
    printf("\n");
}

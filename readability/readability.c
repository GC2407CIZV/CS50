// Analyzes a text and shows which school grade corresponds to the complexity of that text.
#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    // Prompt the user for some text
    string text = get_string("Text: ");
    printf("%s\n", text);

    // Checks text size
    int size = strlen(text);

    // All variables start at counter 0
    int letters = 0;
    int words = 1; // Words starts at 1 because count the total of spaces; 3 spaces = 4 words
    int sentences = 0;

    for (int i = 0; i < size; i++)
    {
        // Checks if it's a letter, if yes add it to the counter.
        if (isalpha(text[i]))
        {
            letters++;
        }
        // Checks if the letter is followed by "," , ".", "?" or "!" If yes adds to the counter
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            sentences++;
        }
        // Check if there is a letter followed by a non-letter, if so: add to the counter.
        if (text[i] == ' ')
        {
            words++;
        }
    }
    // Variable used in the formula
    // Use 1.0 because need to be a float for C-L index (if not use it it will be rounded)
    float L = (1.0 * letters / words) * 100;   // L = average number of letter per 100 words
    float S = (1.0 * sentences / words) * 100; // S = average number of sentences per 100 words

    // Coleman-Liau index: calculates which series is compatible with the analyzed text.
    int index = round(0.0588 * L - 0.296 * S - 15.8); // Round the number to nearest whole number.

    // Print the grade level
    if (index > 16)
    {
        printf("Grade 16+\n");
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", index);
    }
}

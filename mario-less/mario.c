#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int n, i, bricks, s;

    // Ask user for height, only accepts answer from 1 to 8
    do
    {
        n = get_int("Height: ");
    }
    while (n < 1 || n > 8);

    // Follows the program as long as the row nr is smaller than the requiered height
    for (i = 0; i < n; i++)
    {
        // Determine spaces (height - row - 1 (because rows starts at 0))
        // Example: Height of 3; first row is called row 0. So, 3-0-1 (is for the brick)= 2 spaces
        for (s = 0; s < n - i - 1; s++)
        {
            printf(" ");
        }
        // Prints bricks when the column nr = or smaller than the row nr
        // Example: height 3 pyramid, first column is column 0 is smaller than row 2 (because row nr
        // also starts at 0)
        for (bricks = 0; bricks <= i; bricks++)
        {
            printf("#");
        }
        // Go to next row
        printf("\n");
    }
}

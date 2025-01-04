#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define BLOCK_SIZE 512
int main(int argc, char *argv[])
{
    // Check for correct single command-line usage, Print error if not (NOTES)
    if (argc != 2)
    {
        printf("Usage: ./recover FILE\n");
        return 1;
    }
    // Open the memory card
    char *file = argv[1];
    FILE *card = fopen(argv[1], "r");

    // Print error if can't open file
    if (card == NULL)
    {
        printf("Could not open %s! \n", file);
        return 1;
    }

    // Initialize variables
    bool found_jpg = false;
    int jpg_count = 0;

    uint8_t buffer[BLOCK_SIZE]; // Create a buffer for a block of data (NOTES)

    char jpg_name[8];    // Array to store filename of current JPEG found
    FILE *outptr = NULL; // Pointer to current JPEG file

    // While there's still data left to read from the memory card (NOTES)
    while (fread(buffer, 1, BLOCK_SIZE, card) == 512)
    {
        //  Check if block marks start of new JPEG (NOTES)
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            if (found_jpg) // close previous JPEG file
            {
                fclose(outptr);
            }
            else
            {
                found_jpg = true;
            }

            // Open new JPEG file
            // Generate filename for new JPEG image based on jpg_count (NOTES)
            sprintf(jpg_name, "%03d.jpg", jpg_count);
            outptr = fopen(jpg_name, "w"); // Open new JPEG image file with generated filename

            // Print error if new JPEG image file can't be created
            if (outptr == NULL)
            {
                fclose(card);
                printf("Could not create %s.\n", jpg_name);
                return 3;
            }

            jpg_count++; // Increase jpeg_count variable
        }

        // Write current block to current JPEG file if open
        if (found_jpg)
        {
            fwrite(buffer, BLOCK_SIZE, 1, outptr);
        }
    }
    // Close forensic image file and last JPEG if open
    fclose(card);
    if (found_jpg)
    {
        fclose(outptr);
    }
    return 0; // Exit program with 0 to mean success
}

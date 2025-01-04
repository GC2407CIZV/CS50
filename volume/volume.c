// Modifies the volume of an audio file

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Number of bytes in .wav header
const int HEADER_SIZE = 44;

int main(int argc, char *argv[]) // char* = string
{
    // Check command-line arguments
    // Command-line takes 3 arguments (input, output, factor)
    if (argc != 4) // If there are not 4 arguments (./volume, input, output, factor)
    {
        printf("Usage: ./volume input.wav output.wav factor\n");
        return 1; // Exit
    }

    // Open files and determine scaling factor
    FILE *input = fopen(argv[1], "r"); // Argv[1] = input
    if (input == NULL)                 // If the file is NULL => file not found
    {
        printf("Could not open file.\n");
        return 1;
    }

    FILE *output = fopen(argv[2], "w"); // Argv[2] = output
    if (output == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    float factor = atof(argv[3]);

    // TODO: Copy header from input file to output file
    // Create array of bytes not negative
    uint8_t header[HEADER_SIZE]; // Header_size = 44 => total bytes
    fread(header, HEADER_SIZE, 1, input);
    fwrite(header, HEADER_SIZE, 1, output);

    // TODO: Read samples from input file and write updated data to output file
    int16_t buffer;

    // Read single sample into buffer
    while (fread(&buffer, sizeof(int16_t), 1, input))
    {
        // Update volume of sample
        buffer *= factor;

        // Write updated sample to new file
        fwrite(&buffer, sizeof(int16_t), 1, output);
    }

    // Close files
    fclose(input);  // Close input file
    fclose(output); // Close output file
}

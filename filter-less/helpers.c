#include "helpers.h"
#include <math.h>

// Convert image to grayscale // Set RGB to average
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int average =
                (int) ((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0 +
                       0.5);

            image[i][j].rgbtBlue = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtRed = average;
        }
    }
}

// Convert image to sepia // Original RGB values -> set values to sepia (see notes)
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int originalRed = image[i][j].rgbtRed;
            int originalGreen = image[i][j].rgbtGreen;
            int originalBlue = image[i][j].rgbtBlue;

            // Convert Red
            image[i][j].rgbtRed = fmin(255, (int) (0.393 * originalRed + 0.769 * originalGreen +
                                                   0.189 * originalBlue + 0.5));
            // Covert Green
            image[i][j].rgbtGreen = fmin(255, (int) (0.349 * originalRed + 0.686 * originalGreen +
                                                     0.168 * originalBlue + 0.5));
            // Convert Blue
            image[i][j].rgbtBlue = fmin(255, (int) (0.272 * originalRed + 0.534 * originalGreen +
                                                    0.131 * originalBlue + 0.5));
        }
    }
}

// Reflect image horizontally -> Swap the pixel values vertically
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            // Swap the pixel values vertically
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - 1 - j]; // Swaps pixels
            image[i][width - 1 - j] = temp;
        }
    }
}

// Blur image
// New value of each pixel would be the average of the values of all of the pixels that are within 1
// row and column of the original pixel (forming a 3x3 box)
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int totalRed = 0, totalGreen = 0, totalBlue = 0;
            float counter = 0.00;

            for (int x = -1; x < 2; x++)
            {
                for (int y = -1; y < 2; y++)
                {
                    int currentX = i + x;
                    int currentY = j + y;

                    if (currentX < 0 || currentX > (height - 1) || currentY < 0 ||
                        currentY > (width - 1))
                    {
                        continue;
                    }
                    totalRed += image[currentX][currentY].rgbtRed;
                    totalGreen += image[currentX][currentY].rgbtGreen;
                    totalBlue += image[currentX][currentY].rgbtBlue;

                    counter++;
                }
            }
            copy[i][j].rgbtRed = round(totalRed / counter);
            copy[i][j].rgbtGreen = round(totalGreen / counter);
            copy[i][j].rgbtBlue = round(totalBlue / counter);
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = copy[i][j];
        }
    }
    return;
}

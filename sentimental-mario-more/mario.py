from cs50 import get_int

# Ask user for height, only accepts answer from 1 to 8
while True:
    n = get_int("Height: ")

    # Follows the program as long as the row nr is smaller than the requiered height
    if n >= 1 and n <= 8:   # If n is between or equal to 1 and 8
        break  # Stop asking for heigth


for i in range(0, n, 1):  # i starts at '0' will go to the height of 'n' and increase by '1' row
    for j in range(0, n, 1):  # j starts at '0' will go to the height of 'n' and increase by '1' column
        if (i + j < n - 1):
            # end=("") => nothing should be printed at end if don't use it will go to next line
            print(" ", end=(""))
        else:
            print("#", end=(""))
    print("  ", end=(""))  # Space between pyramid
    for r in range(0, n, 1):  # Print the right side of the pyramid
        if (r <= i):
            print("#", end=(""))
    print()  # Go to next row

from cs50 import get_string


text = get_string("Text: ")

letters = 0
words = 1  # Last word doesn't have a space, so + 1
sentences = 0

for i in text:
    if i.isalpha():  # Check if it's a letter
        letters += 1
    if i == " ":  # Check for spaces
        words += 1
    if i == "." or i == "?" or i == "!":  # Check for (. ? !)
        sentences += 1

# Variable used in the formula
# Use 1.0 because need to be a float for C-L index (if not use it it will be rounded)
L = (letters / words) * 100   # L = average number of letter per 100 words
S = (sentences / words) * 100  # S = average number of sentences per 100 words

# Coleman-Liau index: calculates which series is compatible with the analyzed text.
index = 0.0588 * L - 0.296 * S - 15.8  # Round the number to nearest whole number.

if index >= 16:
    print("Grade 16+")
elif index < 1:
    print("Before Grade 1")
else:
    print(f"Grade {round(index)}")

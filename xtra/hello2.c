#include <stdio.h>
#include <cs50.h>

int main(void)
{
//Ask the user his first and last name before replying.
    string first_name = get_string ("What's your first name? ");
    string last_name = get_string ("What is your last name? ");
    printf ("Hello, %s %s. \n", first_name, last_name);
}

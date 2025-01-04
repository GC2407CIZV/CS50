#include <stdio.h>
#include <cs50.h>

int main (void)
{
// Ask the user forhis name, age and phone number.
    string first_name = get_string ("What is your first name? \n");
    string last_name = get_string ("What is your last name? \n");
    int age = get_int ("What is your age? \n");

//Phone number is a string so you can use +, #, -, ... too
    string tel_number = get_string ("What is your phone number? \n");

printf ("Name: %s %s \n", first_name, last_name);
printf ("Age: %i \n", age);
printf ("Phone: %s \n", tel_number);
}

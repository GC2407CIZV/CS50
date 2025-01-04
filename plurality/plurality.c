#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// Candidates have name and vote count
typedef struct
{
    string name;
    int votes;
} candidate; // Data type (votes and names are under candidate)

// Array of candidates
candidate candidates[MAX]; // Data type candidate array name candidates with a max of 9 people

// Number of candidates
int candidate_count;

// Function prototypes
bool vote(string name); // Vote by name and output is true or false (bool)
void print_winner(void);

int main(int argc, string argv[])
{
    // Check for invalid usage
    // In command line: ./plurality (1) alice (2) Bob (3) ...
    // If command is not at least 2; program -> no work
    if (argc < 2)
    {
        printf("Usage: plurality [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1; // -1 = ./plurality
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        // Array but 2 different data inside the array (name + vote)
        candidates[i].name = argv[i + 1]; // i + 1; name starts after ./ plurality in command line
        candidates[i].votes = 0;          // Everyone starts with 0 votes
    }

    int voter_count = get_int("Number of voters: ");

    // Loop over all voters
    for (int i = 0; i < voter_count; i++)
    {
        string name = get_string("Vote: "); // Ask for total voters

        // Check for invalid vote
        if (!vote(name)) // If name is not in the list
        {
            printf("Invalid vote.\n");
        }
    }

    // Display winner of election
    print_winner();
}

// Update vote totals given a new vote
bool vote(string name)
{
    // TODO
    for (int i = 0; i < candidate_count; i++)
    {
        // If the name typed match candidate add a vote
        if (strcmp(name, candidates[i].name) == 0)
        {
            candidates[i].votes++; // Add a vote to candidate
            return true;
        }
    }
    return false;
}

// Print the winner (or winners) of the election
void print_winner(void)
{
    // TODO
    int maxvotes = 0;
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes > maxvotes) // If candidate vote is bigger than maxvote
        {
            maxvotes = candidates[i].votes; // Maxvote updates to a bigger vote
        }
    }
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes == maxvotes) // When both are equal
        {
            printf("%s\n", candidates[i].name); // Print name
        }
    }
    return;
}

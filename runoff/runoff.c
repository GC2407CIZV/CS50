#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max total voters and candidates
#define MAX_VOTERS 100
#define MAX_CANDIDATES 9

// preferences[i][j] is jth preference for voter i
int preferences[MAX_VOTERS][MAX_CANDIDATES];

// Candidates have name, vote count, eliminated status
typedef struct
{
    string name;
    int votes;
    bool eliminated;
} candidate;

// Array of candidates
candidate candidates[MAX_CANDIDATES];

// Numbers of voters and candidates
int voter_count;
int candidate_count;

// Function prototypes
bool vote(int voter, int rank, string name); // Record voter's preference
void tabulate(void);                         // Count votes for remaining candidate
bool print_winner(void);                     // Determine the winner
int find_min(void);      // Find min vote total for candidates not eleminated yet
bool is_tie(int min);    // Check for tie among remaining candidates
void eliminate(int min); // Eleminate candidate with min nr. of votes

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2) // Command-line must be more than 2: ./runoff (1) alice (2)
    {
        printf("Usage: runoff [candidate ...]\n"); // Error message (explain usage)
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1; // (-1 = ./ runoff) total candidates
    if (candidate_count > MAX_CANDIDATES)
    {
        printf("Maximum number of candidates is %i\n", MAX_CANDIDATES);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i].name = argv[i + 1]; // After ./runoff = argv[0] the candidate names start
        candidates[i].votes = 0;          // All votes starts at 0
        candidates[i].eliminated = false; // No-one eleminated yet
    }

    voter_count = get_int("Number of voters: ");
    if (voter_count > MAX_VOTERS)
    {
        printf("Maximum number of voters is %i\n", MAX_VOTERS);
        return 3;
    }

    // Keep querying for votes - Go to every voter
    for (int i = 0; i < voter_count; i++)
    {

        // Query for each rank - go to every candidate
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            // Record vote, unless it's invalid
            if (!vote(i, j, name)) // i = voter, j = nr of candidate, name = candidate name
            {
                printf("Invalid vote.\n"); // Print invalid
                return 4;
            }
        }
        printf("\n"); // Print new line (seperate each voter from eachother)
    }

    // Keep holding runoffs until winner exists
    while (true)
    {
        // Calculate votes given remaining candidates
        tabulate();

        // Check if election has been won
        bool won = print_winner();
        if (won)
        {
            break;
        }

        // Eliminate last-place candidates
        int min = find_min();   // find min votes
        bool tie = is_tie(min); // find ties

        // If tie, everyone wins
        if (tie)
        {
            for (int i = 0; i < candidate_count; i++)
            {
                if (!candidates[i].eliminated)
                {
                    printf("%s\n", candidates[i].name);
                }
            }
            break;
        }

        // Eliminate anyone with minimum number of votes
        eliminate(min);

        // Reset vote counts back to zero (everytime someone is eliminated)
        for (int i = 0; i < candidate_count; i++)
        {
            candidates[i].votes = 0;
        }
    }
    return 0;
}

// Record preference if vote is valid
bool vote(int voter, int rank, string name)
{
    // TODO
    // Track voter, rank, name. Loop through candidate and compare to name
    // If name match, update vote count
    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(candidates[i].name, name) == 0)
        {
            // update preference array of the voter (voter 1 pref. 1 =, pref 2= ,...)
            preferences[voter][rank] = i;
            return true;
        }
    }
    return false;
}

// Tabulate votes for non-eliminated candidates
// Update not eliminated votes number>
// Loop through i+j, not eliminated add count
void tabulate(void)
{
    // TODO
    for (int i = 0; i < voter_count; i++) // Loop through all voters
    {
        for (int j = 0; j < candidate_count; j++) // Loop through all candidates
        {
            // Check if top candidate is eleminated
            if (!candidates[preferences[i][j]].eliminated) // if candidate not eleminated
            {
                candidates[preferences[i][j]].votes++; // add a vote
                break; // Break out of voter to continue or else only count 1 vote
            }
        }
    }
    return;
}

// Print the winner of the election, if there is one
bool print_winner(void)
{
    // TODO
    for (int i = 0; i < candidate_count; i++) // Loop through all candidates
    {
        // If one person has more votes than hald total voters
        if (candidates[i].votes > voter_count / 2)
        {
            printf("%s\n", candidates[i].name);
            return true;
        }
    }
    return false;
}

// Return the minimum number of votes any remaining candidate has
int find_min(void)
{
    // TODO
    int min = voter_count;
    for (int i = 0; i < candidate_count; i++) // Loop through candidates
    {
        // If candidate not eliminated and vote less than min
        if (!candidates[i].eliminated && candidates[i].votes < min)
        {
            min = candidates[i].votes;
        }
    }
    return min;
}

// Return true if the election is tied between all candidates, false otherwise
bool is_tie(int min)
{
    // TODO
    int remaining_candidates = 0;
    int candidates_with_min_votes = 0;
    for (int i = 0; i < candidate_count; i++) // Loop through candidates
    {
        if (!candidates[i].eliminated) // If not eliminated
        {
            remaining_candidates++; // Remaining canditates ++
        }
        if (candidates[i].votes == min)
        {
            candidates_with_min_votes++;
        }
    }
    if (remaining_candidates == candidates_with_min_votes)
    {
        return true;
    }
    return false;
}

// Eliminate the candidate (or candidates) in last place
void eliminate(int min)
{
    // TODO
    for (int i = 0; i < candidate_count; i++) // Loop through candidates
    {
        // If not eliminated and total vote = min
        if (!candidates[i].eliminated && candidates[i].votes == min)
        {
            candidates[i].eliminated = true; // Candidate is eliminated
        }
    }
    return;
}

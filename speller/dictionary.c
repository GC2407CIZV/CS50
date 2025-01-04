// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

char word_length[LENGTH + 1];

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;
int word_count = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO

    int hash_value = hash(word);

    // Create cursor variable
    node *cursor = table[hash_value];

    // Loop until end of linked list
    while (cursor != NULL)
    {
        // Check if the words are same
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        else
        {
            cursor = cursor->next;
        }
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    unsigned long total = 0; // unsigned has to be >= 0
    for (int i = 0; i < strlen(word); i++)
    {
        total += tolower(word[i]);
    }
    return total % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // TODO
    // Clears hash table
    for (int i = 0; i < N; i++)
    {
        table[i] = NULL;
    }

    // Open the dictionary file
    FILE *source = fopen(dictionary, "r");

    // Check if return value is NULL
    if (source == NULL)
    {
        return false;
    }

    // Read each word in the file one at the time
    // fscanf (file, '%s', word)
    while (fscanf(source, "%s", word_length) != EOF)
    {
        // create a new node
        // Use malloc
        node *new_word = malloc(sizeof(node));
        // Check if return value is NULL
        if (new_word == NULL)
        {
            return false;
        }
        // Copy word into node using strcpy
        strcpy(new_word->word, word_length);

        // Use the hash function
        int hash_value = hash(word_length);

        // Check if head is pointing to NULL
        if (table[hash_value] == NULL)
        {
            // Point new_word to NULL
            new_word->next = NULL;
        }
        else
        {
            // otherwise, point new_word to 1st node of linked list
            new_word->next = table[hash_value];
        }
        table[hash_value] = new_word;
        word_count++; // Add each word to the hash table
    }

    // Close the dictionary file
    fclose(source);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO
    // Create temp variable pointer to 1st node
    // Free temp pointer after moving cursor and free temp
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        node *tmp = table[i];

        while (cursor != NULL)
        {
            cursor = cursor->next;
            free(tmp);
            tmp = cursor;
        }
    }
    return true;
}

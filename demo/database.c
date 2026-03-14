#include <stdio.h>
#include <limits.h>
#include <stdbool.h>

#ifndef MAX_USERS
#define MAX_USERS 1000
#endif

/**
 * @brief Initializes the database with a specific capacity.
 * @return bool true if successful, false otherwise.
 */
bool initialize_db(int capacity) {
    if (capacity <= 0) {
        fprintf(stderr, "Error: Invalid capacity.\n");
        return false;
    }
    if (capacity > MAX_USERS) {
        fprintf(stderr, "Error: Capacity too high. Max: %d\n", MAX_USERS);
        return false;
    }
    printf("DB Initialized with capacity: %d\n", capacity);
    return true;
}

/**
 * @brief Safely calculates score with overflow protection.
 * @param points Base points.
 * @param bonus Added bonus.
 * @param multiplier Multiplier factor.
 * @param result Pointer to store the result.
 * @return bool true if calculation is safe, false on overflow.
 */
bool calculate_score(int points, int bonus, int multiplier, int *result) {
    if (!result) return false;

    // Addition Overflow Check
    if ((bonus > 0 && points > INT_MAX - bonus) || (bonus < 0 && points < INT_MIN - bonus)) {
        return false;
    }
    
    int sum = points + bonus;
    long long temp_res = (long long)sum * multiplier;

    // Multiplication Overflow Check
    if (temp_res > INT_MAX || temp_res < INT_MIN) {
        return false;
    }

    *result = (int)temp_res;
    return true;
}

int main() {
    if (!initialize_db(50)) {
        return 1;
    }

    int initial_score = 0;
    if (!calculate_score(10, 5, 2, &initial_score)) {
        fprintf(stderr, "Calculation error: overflow detected.\n");
        return 1;
    }

    printf("System ready. Initial score: %d\n", initial_score);
    return 0;
}

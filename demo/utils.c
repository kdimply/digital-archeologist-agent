#include "utils.h"
#include <limits.h>

/**
 * Calculates the final score with overflow protection.
 * Aligns with the defensive pattern established in math_engine.py.
 */
int calculate_score(int points, int bonus, int multiplier) {
    /* Architectural Context: Promotion to 64-bit prevents intermediate 
       overflow during addition and multiplication. */
    long long sum = (long long)points + bonus;
    long long result = sum * multiplier;

    /* Clamping logic ensures result stays within valid C int bounds,
       mimicking the error-handling safety of the Python engine. */
    if (result > INT_MAX) {
        return INT_MAX;
    }
    if (result < INT_MIN) {
        return INT_MIN;
    }

    return (int)result;
}
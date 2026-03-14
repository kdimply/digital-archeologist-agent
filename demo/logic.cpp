#include <iostream>
#include "utils.h"

int main() {
    int my_points = 100;
    int bonus_points = 50;
    int current_multiplier = 1;

    /* FIX: Updated call to match the 3-argument signature in utils.h.
       This ensures architectural consistency with the math engine's 
       defensive design patterns. */
    int final_score = calculate_score(my_points, bonus_points, current_multiplier); 
    
    std::cout << "Final Score: " << final_score << std::endl;
    return 0;
}
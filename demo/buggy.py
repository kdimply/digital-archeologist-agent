from src.core.math_engine import calculate_velocity

def run_mission_control():
    # BUG 1: It's calling it with only ONE argument (distance).
    # BUG 2: It doesn't handle the potential ValueError for time.
    result = calculate_velocity(100) 
    print(f"Mission Status: {result}")

if __name__ == "__main__":
    run_mission_control()
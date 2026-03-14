# This is the "Truth" file. 
# It lives in a different folder to test Cross-Folder RAG.

def calculate_velocity(distance, time, unit="km/h"):
    """
    Calculates velocity. 
    NOTE: In a recent 'update', we added the 'unit' parameter 
    and made 'time' mandatory to avoid ZeroDivisionError.
    """
    if time <= 0:
        raise ValueError("Time must be greater than zero.")
        
    velocity = distance / time
    return f"{velocity} {unit}"

def get_engine_status():
    return "Math Engine v2.0 - Optimized"
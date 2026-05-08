import pandas as pd
import random

def play_history_game(file_path):
    # Load the dataset
    try:
        df = pd.read_csv(file_path, encoding='latin1')
    except FileNotFoundError:
        print(f"Error: Could not find '{file_path}'. Please ensure the file is in the same folder.")
        return
    except UnicodeDecodeError:
        # Fallback for different Windows encodings
        df = pd.read_csv(file_path, encoding='cp1252')

    # Prepare the list of events
    events_list = df['Event'].tolist()
    
    # Pick a random target event
    target_idx = random.randint(0, len(df) - 1)
    target_row = df.iloc[target_idx]
    target_name = target_row['Event']
    target_year = target_row['Year']

    print("--- Welcome to the Historical Timeline Game! ---")
    print(f"I have chosen a random event from your list of {len(df)} events.")
    print("Your goal is to guess which one it is.")
    print("Each time you guess an event, I will tell you if the target happened BEFORE or AFTER your guess.")
    print("-" * 50)

    attempts = 0
    while True:
        user_input = input("\nEnter the name of a historical event (or 'hint' to see 5 random options): ").strip()
        
        if user_input.lower() == 'hint':
            hints = random.sample(events_list, 5)
            print("Try one of these: " + " | ".join(hints))
            continue

        # Try to find the event in the list (case-insensitive)
        match = df[df['Event'].str.contains(user_input, case=False, na=False, regex=False)]
        
        if match.empty:
            print("I couldn't find that event in the dataset. Try to be more specific or check your spelling.")
            continue
        elif len(match) > 1:
            print(f"Found multiple matches: {', '.join(match['Event'].tolist()[:3])}...")
            print("Please type the full name of the event you intended.")
            continue
        
        # We have a unique match
        attempts += 1
        guess_row = match.iloc[0]
        guess_name = guess_row['Event']
        guess_year = guess_row['Year']

        if guess_name == target_name:
            print(f"\nCONGRATULATIONS! You got it in {attempts} attempts.")
            print(f"The event was: {target_name} ({target_row['Display Year']})")
            break
        
        # Provide feedback based on chronology
        if target_year < guess_year:
            print(f"Target is BEFORE '{guess_name}' ({guess_row['Display Year']})")
        else:
            print(f"Target is AFTER '{guess_name}' ({guess_row['Display Year']})")

if __name__ == "__main__":
    # Ensure this matches your filename exactly
    play_history_game('Historical Events 2.csv')
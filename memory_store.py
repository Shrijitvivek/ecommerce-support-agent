"""
Handles storing and retrieving persistent customer preferrences.
"""
import json # needed for json.loads
import os # needed for os.path.join

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') # path to data directory    
PREFERENCES_FILE = os.path.join(DATA_DIR, 'preferences.json') # path to preferences file


def _load_preferences():
    with open(PREFERENCES_FILE, "r", encoding="utf-8") as f: # open preferences file
        return json.load(f) # load preferences from file

# function to save preference
def save_preference(user_id , preference):
    preferences = _load_preferences() # load preferences

    preferences[user_id] = { # update preferences
        "preferred_resolution": preference
    }

    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f: # open preferences file
        json.dump(preferences, f, indent=2) # save preferences

# function to get preference
def get_preference(user_id):
    preferences = _load_preferences() # load preferences

    user_preference = preferences.get(user_id) # get user preference

    if user_preference: # if user preference exists
        return user_preference["preferred_resolution"] # return user preference

    return None

if __name__ == "__main__":
    save_preference("user_001", "replacement")
    print(get_preference("user_001"))

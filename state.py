import json
import os

STATE_FILE = 'data/state.json'
ERAS_FILE = 'data/eras.json'

def load_eras():
    with open(ERAS_FILE, 'r') as f:
        return json.load(f)

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    os.makedirs('data', exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def new_game(era="Mesozoic", period="Cretaceous"):
    """Create a new game and populate state with era/period details."""
    eras = load_eras()
    details = eras[era][period]
    state = {
        "era": era,
        "period": period,
        "environment": details["environment"],
        "fauna": details["fauna"],
        "flora": details["flora"],
        "events": details["events"],
        "player": {
            "name": "",
            "profession": "",
            "strengths": [],
            "weaknesses": [],
            "ability": "",
            "skills": [],
            "llm_profile": ""
        },
        "turn": 0
    }
    save_state(state)
    return state

def update_period(state, era, period):
    """Change the current era/period and update environment/fauna/flora/events."""
    eras = load_eras()
    details = eras[era][period]
    state['era'] = era
    state['period'] = period
    state['environment'] = details['environment']
    state['fauna'] = details['fauna']
    state['flora'] = details['flora']
    state['events'] = details['events']
    save_state(state)
    return state

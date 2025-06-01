from llama_client import stream_llm
from state import load_state, save_state, new_game, update_period, load_eras
from prompts import make_prompt, character_creation_prompt
import json
import re

# --- Optional: Use wordninja for super-clean word splitting ---
try:
    import wordninja
    USE_WORDNINJA = True
except ImportError:
    USE_WORDNINJA = False

def fix_spacing(text):
    # Regex: Add space between a lower/number and upper (e.g., "AsYour" => "As Your")
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    # Regex: Add space after periods if not already present
    text = re.sub(r'\.([A-Za-z])', r'. \1', text)
    # Optional: use wordninja to split very long mashed words
    if USE_WORDNINJA:
        def fix_long_word(word):
            if len(word) > 12:
                return ' '.join(wordninja.split(word))
            return word
        lines = []
        for line in text.split('\n'):
            fixed_words = [fix_long_word(w) for w in re.findall(r"[A-Za-z0-9']+|[^\w\s]", line)]
            lines.append(' '.join(fixed_words))
        text = '\n'.join(lines)
    return text

def format_llm_output(text):
    # Convert literal '\n' to real newlines and normalize
    text = text.replace('\\n', '\n').replace('\r\n', '\n')
    # Optional: Wrap lines > 150 chars for console readability
    lines = []
    for paragraph in text.split('\n'):
        while len(paragraph) > 150:
            break_at = paragraph.rfind(' ', 0, 150)
            if break_at == -1:
                break_at = 150
            lines.append(paragraph[:break_at])
            paragraph = paragraph[break_at:].strip()
        lines.append(paragraph)
    return '\n'.join(lines)

import re

def extract_characteristics_from_output(text):
    # This function extracts the first traits/skills/ability/weaknesses found in prose
    strengths, weaknesses, ability, skills = [], [], "", []

    # Lowercase version for matching
    t = text.lower()

    # Strengths: look for lines with "strengths" or "strength"
    strengths_match = re.search(r"(?:strengths? (?:include|are|:|which include|which are)\s*)([a-z ,\-]+?)[\.\n]", t)
    if strengths_match:
        items = strengths_match.group(1)
        # split on 'and', 'or', ',', or ' as well as '
        for i in re.split(r',| and | or | as well as ', items):
            trait = i.strip(" .,-")
            if trait and trait not in strengths:
                strengths.append(trait.capitalize())

    # Weaknesses
    weaknesses_match = re.search(r"(?:weaknesses? (?:include|are|:|which include|which are)\s*)([a-z ,\-]+?)[\.\n]", t)
    if weaknesses_match:
        items = weaknesses_match.group(1)
        for i in re.split(r',| and | or | as well as ', items):
            trait = i.strip(" .,-")
            if trait and trait not in weaknesses:
                weaknesses.append(trait.capitalize())

    # Ability (first "unique ability" or "unique aspect" or "my ability is")
    ability_match = re.search(r"(?:unique (?:ability|aspect)[^\w]{0,3}|my ability is\s*)([a-zA-Z \-]+?)[\.\n]", t)
    if ability_match:
        ability = ability_match.group(1).strip(" .,-").capitalize()

    # Skills (first "skills include" or "skills are")
    skills_match = re.search(r"(?:skills (?:include|are|:)\s*)([a-z ,\-]+?)[\.\n]", t)
    if skills_match:
        items = skills_match.group(1)
        for i in re.split(r',| and | or | as well as ', items):
            trait = i.strip(" .,-")
            if trait and trait not in skills:
                skills.append(trait.capitalize())

    return strengths, weaknesses, ability, skills


def create_character(state):
    print("CHRONOS: Welcome aboard the Chronos Explorer! What is your name, traveler?")
    name = input("Name: ").strip()
    print("CHRONOS: And your profession? (e.g., Biologist, Engineer, Hunter, Geologist, etc.)")
    profession = input("Profession: ").strip()
    prompt = character_creation_prompt(name, profession)
    print("\nGenerating your explorer profile...\n")
    llm_output = ""
    for chunk in stream_llm(prompt):
        llm_output += chunk  # No print, just collect

    # Fix up output for readability and trait parsing
    cleaned_output = format_llm_output(llm_output)
    cleaned_output = fix_spacing(cleaned_output)
    strengths, weaknesses, ability, skills = extract_characteristics_from_output(cleaned_output)

    state['player']['name'] = name
    state['player']['profession'] = profession
    state['player']['strengths'] = strengths
    state['player']['weaknesses'] = weaknesses
    state['player']['ability'] = ability
    state['player']['skills'] = skills
    state['player']['llm_profile'] = cleaned_output
    save_state(state)
    print("\nCharacter created successfully!\n")
    print("\nCHRONOS:\n" + cleaned_output)
    return state

def choose_era_and_period():
    eras = load_eras()
    print("\nChoose an era:")
    era_list = list(eras.keys())
    for idx, era in enumerate(era_list):
        print(f"{idx+1}: {era}")
    era_choice = int(input("Era number: ")) - 1
    era = era_list[era_choice]
    periods = list(eras[era].keys())
    print(f"\nChoose a period in the {era} era:")
    for idx, period in enumerate(periods):
        print(f"{idx+1}: {period}")
    period_choice = int(input("Period number: ")) - 1
    period = periods[period_choice]
    return era, period

def main():
    state = load_state()
    if state is None or not state['player']['name']:
        print("Start a new game? (y/n)")
        if input("> ").strip().lower() == "y":
            era, period = choose_era_and_period()
            state = new_game(era, period)
            state = create_character(state)
        else:
            print("Exiting.")
            return
    print("CHRONOS: Initializing survival simulation. Good luck!\n")
    while True:
        print(f"\nEra: {state['era']} | Period: {state['period']} | Turn: {state['turn']}")
        print(f"Environment: {state['environment']}")
        print(f"Dominant Fauna: {', '.join(state['fauna'])}")
        print(f"Dominant Flora: {', '.join(state['flora'])}")
        print(f"Major Events: {', '.join(state['events'])}")
        print(f"Player: {state['player']['name']} ({state['player']['profession']})")
        print(f"Stats: Strengths: {state['player']['strengths']} | Weaknesses: {state['player']['weaknesses']}")
        print(f"Ability: {state['player']['ability']} | Skills: {state['player']['skills']}")
        print("\nWhat will you do?")
        print("Type 'change period' to travel to a new era/period, or 'quit' to exit.")
        action = input("> ")
        if action.lower() in ['quit', 'exit']:
            save_state(state)
            print("CHRONOS: Game saved. See you next time!")
            break
        if action.lower() == 'change period':
            era, period = choose_era_and_period()
            state = update_period(state, era, period)
            continue
        prompt = make_prompt(state, action)
        response_text = ""
        for chunk in stream_llm(prompt):
            response_text += chunk
        # Clean up LLM output before displaying
        readable_output = format_llm_output(response_text)
        readable_output = fix_spacing(readable_output)
        print("\nCHRONOS:\n" + readable_output)
        state['turn'] += 1
        save_state(state)

if __name__ == "__main__":
    main()

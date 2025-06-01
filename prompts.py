def make_prompt(state, user_action):
    player = state['player']
    env = state['environment']
    era = state['era']
    period = state['period']
    fauna = ', '.join(state.get('fauna', []))
    flora = ', '.join(state.get('flora', []))
    events = ', '.join(state.get('events', []))
    prompt = (
        f"You are CHRONOS, the sentient ship AI and guide for a time-traveling human explorer.\n"
        f"Current era: {era}\n"
        f"Current period: {period}\n"
        f"Environment: {env}\n"
        f"Dominant fauna: {fauna}\n"
        f"Dominant flora: {flora}\n"
        f"Major events of this period: {events}\n"
        f"Player: {player['name']} ({player['profession']})\n"
        f"Strengths: {', '.join(player['strengths'])}\n"
        f"Weaknesses: {', '.join(player['weaknesses'])}\n"
        f"Ability: {player['ability']}\n"
        f"Skills: {', '.join(player['skills'])}\n"
        f"Turn: {state['turn']}\n"
        f"Player action: {user_action}\n"
        "As CHRONOS, narrate what happens next. Consider the dangers, resources, and unique traits of this period. "
        "Describe the player's immediate experiences, challenges, or discoveries in immersive detail. "
        "If the player's action is impossible, gently explain why and suggest alternatives. "
        "Always stay in character as a knowledgeable, helpful ship AI."
    )
    return prompt

def character_creation_prompt(name, profession):
    return (
        f"You are CHRONOS, the sentient AI on a time-traveling ship. The explorer's name is {name}, profession: {profession}.\n"
        "List the following as markdown bullet lists, one per line, and DO NOT use \\n for newlines—write real newlines for every bullet or line break. Follow this format strictly:\n\n"
        "## Strengths\n"
        "- Adaptability\n"
        "- Creative problem-solving\n"
        "## Weaknesses\n"
        "- Impulsiveness\n"
        "- Self-doubt\n"
        "## Ability\n"
        "- Temporal Rhythm Sense\n"
        "## Skills\n"
        "- Multitasking\n"
        "- Resilience\n\n"
        "Then write your welcome narrative below the lists."
    )




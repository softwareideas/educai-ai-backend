from typing import Dict

# Delayed imports to avoid heavy initialization at module import time

def load_all_agents() -> Dict[str, object]:
    from educai.agents.medical.general import create_agent as general_agent
    from educai.agents.medical.group_agents import load_group_agents

    # Core set: general + grouped subject agents (preclinical, paraclinical, clinical, diagnostic, superspecialty, allied_health, neet_core)
    agents = {
        'general': general_agent(),
    }
    agents.update(load_group_agents())
    return agents

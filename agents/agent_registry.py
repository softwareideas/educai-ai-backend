from typing import Dict

# Delayed imports to avoid heavy initialization at module import time

def load_all_agents() -> Dict[str, object]:
    from agents.medical.anatomy import create_agent as anatomy_agent
    from agents.medical.physiology import create_agent as physiology_agent
    from agents.medical.biochemistry import create_agent as biochemistry_agent
    from agents.medical.pathology import create_agent as pathology_agent
    from agents.medical.pharmacology import create_agent as pharmacology_agent
    from agents.medical.general import create_agent as general_agent

    agents = {
        'anatomy': anatomy_agent(),
        'physiology': physiology_agent(),
        'biochemistry': biochemistry_agent(),
        'pathology': pathology_agent(),
        'pharmacology': pharmacology_agent(),
        'general': general_agent(),
    }
    return agents

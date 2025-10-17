from typing import Optional
from educai.agents.agent_system import MedicalAgentSystem
from educai.agents.teaching import WorldClassMedicalTeachingSystem
from educai.agents.manager import ManagerAgent

_agent_system: Optional[MedicalAgentSystem] = None
_teaching_system: Optional[WorldClassMedicalTeachingSystem] = None
_manager_agent: Optional[ManagerAgent] = None


def get_agent_system() -> MedicalAgentSystem:
    global _agent_system
    if _agent_system is None:
        _agent_system = MedicalAgentSystem()
    return _agent_system


def get_teaching_system() -> WorldClassMedicalTeachingSystem:
    global _teaching_system
    if _teaching_system is None:
        _teaching_system = WorldClassMedicalTeachingSystem()
    return _teaching_system


def get_manager_agent() -> ManagerAgent:
    global _manager_agent
    if _manager_agent is None:
        _manager_agent = ManagerAgent()
    return _manager_agent

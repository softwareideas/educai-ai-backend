from typing import Optional
from agents.medical_agents import MedicalAgentSystem
from agents.enhanced_teaching_agent import WorldClassMedicalTeachingSystem

_agent_system: Optional[MedicalAgentSystem] = None
_teaching_system: Optional[WorldClassMedicalTeachingSystem] = None


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

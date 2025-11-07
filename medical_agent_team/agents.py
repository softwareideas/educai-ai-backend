from typing import Dict

from app.config import GEMINI_MODEL
from medical_agent_team.agent_factory import AgentCreator
from medical_agent_team.prompts.manager import INSTRUCTION as MANAGER_PROMPT
from medical_agent_team.prompts.report import INSTRUCTION as REPORT_PROMPT
from medical_agent_team.prompts.report_neet import INSTRUCTION as REPORT_NEET_PROMPT
from medical_agent_team.prompts.websearch import INSTRUCTION as WEB_PROMPT
from medical_agent_team.prompts.general import INSTRUCTION as GENERAL_PROMPT
from medical_agent_team.prompts.physics import INSTRUCTION as PHYSICS_PROMPT
from medical_agent_team.prompts.chemistry import INSTRUCTION as CHEM_PROMPT
from medical_agent_team.prompts.medical.anatomy import INSTRUCTION as ANATOMY_PROMPT
from medical_agent_team.prompts.medical.physiology import INSTRUCTION as PHYSIO_PROMPT
from medical_agent_team.prompts.medical.biochemistry import INSTRUCTION as BIOCHEM_PROMPT
from medical_agent_team.prompts.medical.pathology import INSTRUCTION as PATHO_PROMPT
from medical_agent_team.prompts.medical.pharmacology import INSTRUCTION as PHARMA_PROMPT
from medical_agent_team.tools.web import web_search
from medical_agent_team.tools.fetch import fetch_url_content
from medical_agent_team.tools.report import build_report

def create_manager_and_team(model: str = GEMINI_MODEL) -> Dict[str, object]:
    creator = AgentCreator(model=model)

    # Define all agents with enhanced descriptions - all have web_search tool
    anatomy = creator._initialize_agent(
        name="anatomy_agent",
        description="Expert in human anatomical structures, relationships, blood supply, innervation, and clinical anatomy. Handles questions about gross anatomy, neuroanatomy, vascular anatomy, musculoskeletal anatomy, and surface landmarks.",
        instruction=ANATOMY_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    physiology = creator._initialize_agent(
        name="physiology_agent",
        description="Expert in organ system physiology, homeostatic mechanisms, regulatory systems, and pathophysiological processes. Handles questions about body functions, control systems, feedback loops, and physiological mechanisms.",
        instruction=PHYSIO_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    biochemistry = creator._initialize_agent(
        name="biochemistry_agent",
        description="Expert in metabolic pathways, enzyme mechanisms, biochemical processes, and clinical biochemistry. Handles questions about glycolysis, TCA cycle, energy metabolism, enzyme kinetics, and biochemical basis of disease.",
        instruction=BIOCHEM_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    pathology = creator._initialize_agent(
        name="pathology_agent",
        description="Expert in disease mechanisms, morphological changes, histopathology, and diagnostic pathology. Handles questions about disease etiology, pathogenesis, gross/microscopic pathology, and pathological correlations with clinical features.",
        instruction=PATHO_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    pharmacology = creator._initialize_agent(
        name="pharmacology_agent",
        description="Expert in drug mechanisms, pharmacokinetics, pharmacodynamics, and clinical pharmacology. Handles questions about drug classes, mechanisms of action, adverse effects, drug interactions, and therapeutic uses.",
        instruction=PHARMA_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    web_agent = creator._initialize_agent(
        name="web_search_agent",
        description="Specialized agent for finding authoritative medical information from reputable online sources including WHO, CDC, NIH, major medical journals, and specialty societies. Prioritizes quality and accuracy over quantity.",
        instruction=WEB_PROMPT,
        tools=[web_search],
    )
    general_agent = creator._initialize_agent(
        name="general_specialist_agent",
        description="General medical explainer and synthesizer. Uses web search and content fetching to ground explanations when no single specialist fits.",
        instruction=GENERAL_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    physics_agent = creator._initialize_agent(
        name="physics_agent",
        description="Physics specialist: mechanics, E&M, waves/optics, thermal, modern physics; grounded, formula-forward explanations.",
        instruction=PHYSICS_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    chemistry_agent = creator._initialize_agent(
        name="chemistry_agent",
        description="Chemistry specialist: physical/inorganic/organic/analytical chemistry; mechanisms, equations, and conditions explained clearly.",
        instruction=CHEM_PROMPT,
        tools=[web_search, fetch_url_content],
    )
    summary_agent_general = creator._initialize_agent(
        name="summary_agent_general",
        description="General-mode summary agent: produces student-friendly, bullet-first summaries with formula sections and high readability.",
        instruction=REPORT_PROMPT,
        tools=[build_report],
    )
    summary_agent_neet = creator._initialize_agent(
        name="summary_agent_neet",
        description="NEET-mode summary agent: high-yield bullets, equations, mnemonics, exam traps, and possible questions.",
        instruction=REPORT_NEET_PROMPT,
        tools=[build_report],
    )

    sub_agents = [
        anatomy,
        physiology,
        biochemistry,
        pathology,
        pharmacology,
        physics_agent,
        chemistry_agent,
        web_agent,
        summary_agent_general,
        summary_agent_neet,
        general_agent,
    ]

    manager_tools = [web_search, fetch_url_content, build_report]

    manager = creator._initialize_agent(
        name="orchestrator_agent",
        description="Orchestrator: analyzes questions, delegates to the best specialist (or general specialist fallback), fetches evidence, and routes to the appropriate summary agent (general or NEET) for final report formatting.",
        instruction=MANAGER_PROMPT,
        tools=manager_tools,
        sub_agents=sub_agents,
    )

    return {
        "manager": manager,
        "root_agent": manager,
    }

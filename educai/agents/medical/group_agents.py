from typing import Dict
from educai.agents.base import MedicalAgent


def _make_agent(agent_id: str, name: str, specialization: str, description: str, extra: str = "") -> MedicalAgent:
    system_prompt = (
        f"You are a highly knowledgeable Medical Expert: {name}. "
        f"Role: {description}. "
        f"Provide accurate, concise, well-structured explanations with bullet points and short tables when useful. "
        f"Focus on foundational concepts, mechanisms, clinical relevance, and exam-ready clarity. {extra}"
    )
    return MedicalAgent(
        agent_id=agent_id,
        name=name,
        specialization=specialization,
        description=description,
        system_prompt=system_prompt,
    )


def load_group_agents() -> Dict[str, MedicalAgent]:
    agents: Dict[str, MedicalAgent] = {}

    # 1) Pre‑Clinical
    agents["preclinical"] = _make_agent(
        "preclinical",
        "Pre‑Clinical Agent",
        "Anatomy, Physiology, Biochemistry",
        "Handles MBBS 1st year / NEET foundation topics across Anatomy, Physiology, and Biochemistry.",
        extra=(
            " Emphasize integrated basic sciences and NEET/MBBS foundational clarity."
            " Provide concise definitions, key mechanisms, summary tables, and common pitfalls."
            " Where relevant, include mnemonics and a few MCQ-style checks (2–3 items)."
        ),
    )

    # 2) Para‑Clinical
    agents["paraclinical"] = _make_agent(
        "paraclinical",
        "Para‑Clinical Agent",
        "Pathology, Microbiology, Pharmacology, Forensic Medicine, Community Medicine",
        "Handles MBBS 2nd year topics including Pathology, Microbiology, Pharmacology, Forensic Medicine & Toxicology, Community Medicine (PSM).",
        extra=(
            " Highlight mechanisms (pathogenesis), lab diagnosis frameworks, drug MOA/ADR/CI/dosing, and core public health principles."
            " Use micro → patho → pharma linkage where helpful; add short case snippets."
        ),
    )

    # 3) Clinical
    agents["clinical"] = _make_agent(
        "clinical",
        "Clinical Agent",
        "Medicine, Surgery, Pediatrics, OBG, Orthopedics, ENT, Ophthalmology, Dermatology, Psychiatry, Pulmonology",
        "Handles clinical scenarios, history/exam, differential diagnosis, investigations, and management across core clinical subjects.",
        extra=(
            " Use case-based reasoning and a stepwise clinical approach (Hx → Ex → DDx → Ix → Mx)."
            " Provide red flags and initial stabilization steps when appropriate."
        ),
    )

    # 4) Diagnostic & Supportive
    agents["diagnostic"] = _make_agent(
        "diagnostic",
        "Diagnostic & Supportive Agent",
        "Radiology, Anesthesiology, Emergency Medicine, Nuclear Medicine, Lab Medicine",
        "Handles diagnostics, imaging interpretation basics, perioperative/anesthesia, emergency care, and nuclear medicine principles.",
        extra=(
            " Provide succinct interpretation frameworks (e.g., systematic CXR/ECG reads), checklists, and safety considerations."
            " Keep guidance practical and protocol-aware."
        ),
    )

    # 5) Super‑Specialty
    agents["superspecialty"] = _make_agent(
        "superspecialty",
        "Super‑Specialty Agent",
        "Cardiology, Nephrology, Gastroenterology, Neurology, Oncology, Endocrinology, etc.",
        "Handles high‑level overviews and foundations for super‑specialty disciplines.",
        extra=(
            " Keep content accessible for senior MBBS/PG entrance prep with algorithmic overviews, scoring systems, and key trials where applicable."
        ),
    )

    # 6) Allied Health & Paramedical
    agents["allied_health"] = _make_agent(
        "allied_health",
        "Allied Health & Paramedical Agent",
        "Nursing, Physiotherapy, MLT, Radiography, OTT, Anesthesia Technology, Dialysis Tech, Optometry, OT, Dentistry, Pharmacy, Nutrition, Public Health, HIM, Biomedical Engineering",
        "Covers paramedical and allied health foundational topics and guidance.",
    )

    # 7) NEET Core (Biology umbrella)
    agents["neet_core"] = _make_agent(
        "neet_core",
        "NEET Core Agent",
        "NEET Biology (Zoology + Botany) basics",
        "Handles NEET Biology core including human/plant biology, physiology, genetics, ecology, and high‑yield topics.",
        extra=(
            " Provide MCQ‑ready notes, mnemonics, high‑yield tables, and quick‑revision tips."
            " Be concise and exam-oriented; suggest 2–3 practice MCQs when helpful."
        ),
    )

    return agents

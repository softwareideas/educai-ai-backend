from typing import Dict, List, Tuple
from educai.agents.base import MedicalAgent


def create_specialty_agent(agent_id: str, name: str, specialization: str, description: str, prompt_extra: str = "") -> MedicalAgent:
    system_prompt = (
        f"You are a highly knowledgeable Medical Expert in {name}. "
        f"Provide accurate, concise, and clinically relevant explanations. "
        f"Focus on foundational concepts, mechanisms, symptoms/signs (where applicable), diagnosis, and management principles. "
        f"Use clear structure, bullets, and short tables when useful. {prompt_extra}"
    )
    return MedicalAgent(
        agent_id=agent_id,
        name=name,
        specialization=specialization,
        description=description,
        system_prompt=system_prompt,
    )


def load_specialty_agents() -> Dict[str, MedicalAgent]:
    # Define specialties: (id, name, specialization, description)
    specs: List[Tuple[str, str, str, str]] = [
        # Para-clinical additions
        ("microbiology", "Microbiology", "Infectious diseases & microbes", "Bacteria, viruses, fungi, parasites; pathogenesis, lab diagnosis, prevention"),
        ("forensic_medicine", "Forensic Medicine & Toxicology", "Legal medicine & toxicology", "Medico-legal aspects, injuries, poisonings, forensic procedures"),
        ("community_medicine", "Community Medicine (PSM)", "Public health & epidemiology", "Epidemiology, screening, immunization, health programs, biostatistics"),
        # Clinical branches
        ("general_medicine", "General & Internal Medicine", "Adult medicine", "History, examination, differential diagnosis, investigations, management"),
        ("pediatrics", "Pediatrics", "Child health", "Growth & development, pediatric diseases, vaccinations, neonatal care"),
        ("dermatology", "Dermatology", "Skin & venereal diseases", "Dermatoses, infections, STDs, diagnostics and management"),
        ("psychiatry", "Psychiatry", "Mental health", "Psychiatric disorders, assessment, counseling, pharmacotherapy"),
        ("pulmonology", "Respiratory Medicine (Pulmonology)", "Lung & airway", "Asthma, COPD, TB, ILD, sleep disorders, diagnostics & therapy"),
        # Surgical branches
        ("general_surgery", "General Surgery", "Surgical principles", "Pre/post-op care, wound healing, common procedures, GI surgery"),
        ("orthopedics", "Orthopedics", "Bones & joints", "Fractures, dislocations, arthritis, ortho emergencies, imaging"),
        ("ophthalmology", "Ophthalmology", "Eye", "Anatomy, refraction, cataract, glaucoma, retina, neuro-ophthalmology"),
        ("ent", "ENT", "Ear, Nose, Throat", "Otology, rhinology, laryngology, head & neck basics"),
        ("plastic_surgery", "Plastic & Reconstructive Surgery", "Reconstruction", "Burns, grafts, flaps, hand & craniofacial basics"),
        ("neurosurgery", "Neurosurgery", "Neurosurgical basics", "Head injury, spine, tumors—principles and pathways"),
        ("cardiothoracic_surgery", "Cardiothoracic Surgery", "Heart & thoracic", "Cardiac & thoracic surgical conditions and care principles"),
        ("urology", "Urology", "Urinary tract & male reproductive", "Stones, BPH, malignancies, infections"),
        # OBG
        ("obstetrics", "Obstetrics", "Pregnancy & childbirth", "Antenatal care, labor, complications, obstetric emergencies"),
        ("gynecology", "Gynaecology", "Female reproductive health", "Menstrual disorders, infertility, tumors, infections"),
        # Diagnostic & supportive
        ("radiology", "Radiology", "Imaging", "X-ray, CT, MRI, USG—indications, interpretation fundamentals"),
        ("anesthesiology", "Anesthesiology", "Anesthesia & perioperative care", "Airway, anesthesia techniques, monitoring, ICU basics"),
        ("emergency_medicine", "Emergency Medicine", "Acute care", "Resuscitation, trauma, toxicology, acute presentations"),
        ("nuclear_medicine", "Nuclear Medicine", "Molecular imaging & therapy", "Radionuclide imaging & therapeutics basics"),
        # Super-specialties
        ("cardiology", "Cardiology", "Heart", "Cardiac physiology & pathology, ECG, ischemic heart disease, heart failure"),
        ("nephrology", "Nephrology", "Kidney", "AKI/CKD, electrolytes, acid-base, dialysis principles"),
        ("gastroenterology", "Gastroenterology", "GI & liver", "GI disorders, endoscopy basics"),
        ("neurology", "Neurology", "Nervous system", "Stroke, epilepsy, movement disorders, neuromuscular"),
        ("oncology", "Oncology", "Cancer medicine", "Tumor biology, staging, chemo/radiotherapy principles"),
        ("endocrinology", "Endocrinology", "Hormones & metabolism", "Diabetes, thyroid, adrenal, pituitary"),
        ("pediatric_surgery", "Pediatric Surgery", "Children's surgery", "Congenital anomalies, pediatric emergencies"),
        ("vascular_surgery", "Vascular Surgery", "Vessels", "Aneurysm, PAD, varicose veins—principles"),
        ("hepatology", "Hepatology", "Liver", "Hepatitis, cirrhosis, portal HTN basics"),
        ("critical_care", "Critical Care Medicine", "ICU", "Shock, ventilation, sepsis bundles, organ support"),
        ("rheumatology", "Rheumatology", "Joints & immunity", "Arthritides, autoimmune diseases, immunomodulators"),
        ("pulmonary_critical_care", "Pulmonary & Critical Care", "ICU lung", "ARDS, ventilation, weaning, critical pulmonary"),
        ("hematology", "Hematology", "Blood", "Anemias, leukemias, coagulopathies"),
        ("neonatology", "Neonatology", "Newborn care", "Prematurity, resuscitation, NICU basics"),
        # Allied & paramedical
        ("nursing", "Nursing", "Nursing science", "Patient care principles, nursing procedures"),
        ("physiotherapy", "Physiotherapy", "Rehabilitation", "Therapeutic exercise, rehab plans"),
        ("mlt", "Medical Laboratory Technology", "Lab technology", "Sample handling, lab techniques, QA"),
        ("radiography", "Radiography / Imaging Technology", "Imaging tech", "Imaging equipment & safety"),
        ("ott", "Operation Theatre Technology", "OT technology", "OT procedures, asepsis, instruments"),
        ("anesthesia_technology", "Anesthesia Technology", "Anesthesia tech", "Equipment, monitoring, safety"),
        ("dialysis_technology", "Dialysis Technology", "Renal replacement tech", "Dialysis operation, safety, troubleshooting"),
        ("optometry", "Optometry", "Vision science", "Refraction, optics, low vision care"),
        ("occupational_therapy", "Occupational Therapy", "Functional rehab", "ADL training, ergonomics"),
        ("dental", "Dentistry / Dental Hygiene", "Oral health", "Dental anatomy, caries, periodontal basics"),
        ("pharmacy", "Pharmacy", "Pharmaceutical sciences", "Pharmacology, dispensing, pharmaceutics basics"),
        ("nutrition_dietetics", "Nutrition & Dietetics", "Nutrition", "Macros/micros, diet planning, clinical nutrition"),
        ("public_health", "Public Health (BPH/MPH)", "Public health", "Epidemiology, programs, policy"),
        ("him", "Health Information Management", "Health informatics", "Records, data, privacy"),
        ("biomedical_engineering", "Biomedical Engineering", "MedTech", "Medical devices, sensors, safety"),
        # NEET Biology umbrella (plants, ecology, cell & molecular, etc.)
        ("neet_biology", "NEET Biology", "Biology for NEET", "Human & plant biology, physiology, genetics, ecology topics per NEET syllabus"),
    ]

    agents: Dict[str, MedicalAgent] = {}
    for sid, name, spec, desc in specs:
        extra = ""
        if sid == "neet_biology":
            extra = (
                " Cover human biology plus plant biology (photosynthesis, respiration in plants, transport, growth), "
                "cell & molecular biology (cell, biomolecules, enzymes, cell cycle), genetics & evolution, reproduction, and ecology."
            )
        agents[sid] = create_specialty_agent(sid, name, spec, desc, prompt_extra=extra)
    return agents

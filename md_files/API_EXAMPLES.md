# 🚀 API Examples & Testing Guide

## Quick Start

### 1. Start the Server

```bash
cd d:\Edu-tec\medical_agents_project
python app.py
```

Server will run on: `http://localhost:8080`

### 2. Test Basic Endpoint

```bash
# Get API information
curl http://localhost:8080/
```

---

## 📚 Teaching Modes Examples

### 1. Explain Mode (Comprehensive Learning)

**Use when**: You want a detailed, thorough explanation

```bash
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the mechanism of action potential in neurons",
    "mode": "explain",
    "difficulty": "intermediate"
  }'
```

**Response includes**:

- Core concept definition
- Detailed explanation with mechanisms
- Clinical relevance
- Key takeaways
- Memory aids
- Related concepts

---

### 2. Socratic Mode (Active Learning)

**Use when**: You want to develop critical thinking

```bash
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does insulin regulate blood glucose?",
    "mode": "socratic",
    "difficulty": "intermediate"
  }'
```

**Response includes**:

- Guiding questions (3-4 progressive)
- Think-about prompts
- Learning path
- Reasoning confirmation

---

### 3. Clinical Case Mode (Application Learning)

**Use when**: You want to apply knowledge to real scenarios

```bash
curl -X POST http://localhost:8080/clinical-case \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Acute myocardial infarction"
  }'
```

**Response includes**:

- Patient presentation (age, sex, chief complaint)
- History and examination findings
- Clinical reasoning guide
- Investigation results with lab values
- Diagnosis and management
- Teaching points and NEET relevance

---

### 4. Mnemonic Mode (Memory Aids)

**Use when**: You need to memorize lists, facts, or sequences

```bash
curl -X POST http://localhost:8080/mnemonic \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Branches of the aortic arch"
  }'
```

**Another example**:

```bash
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Essential amino acids",
    "mode": "mnemonic",
    "agent": "biochemistry"
  }'
```

**Response includes**:

- Primary mnemonic (catchy acronym)
- Visual memory aid
- Association chains
- Pattern recognition
- Quick recall test
- NEET tip

---

### 5. Quiz Mode (Practice & Assessment)

**Use when**: You want to test your knowledge

```bash
curl -X POST http://localhost:8080/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Cardiac physiology",
    "difficulty": "advanced"
  }'
```

**Response includes**:

- 5 NEET-style MCQs
- Detailed explanations for correct answers
- Why each wrong option is incorrect
- Concepts tested
- NEET pearls
- Related topics
- Performance analysis

---

### 6. Differential Diagnosis Mode (Clinical Reasoning)

**Use when**: You want to train diagnostic thinking

```bash
curl -X POST http://localhost:8080/differential \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "A 60-year-old male presents with progressive shortness of breath and pedal edema"
  }'
```

**Response includes**:

- Chief complaint analysis
- Differential diagnosis (VINDICATE framework)
- Systematic approach with supporting/refuting features
- Diagnostic workup strategy
- Red flags
- Clinical pearls

---

### 7. Step-by-Step Mode (Breaking Down Complexity)

**Use when**: A topic feels too complex or overwhelming

```bash
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the electron transport chain",
    "mode": "step_by_step",
    "agent": "biochemistry"
  }'
```

**Response includes**:

- Prerequisite knowledge check
- Step 1: Foundation
- Step 2: Building up
- Step 3: Integration
- Step 4: Application
- Common confusion points
- Visual summary
- What you now understand

---

### 8. NEET-Focused Mode (Exam Strategy)

**Use when**: Preparing specifically for NEET exam

```bash
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Thyroid hormone synthesis and regulation",
    "mode": "neet_focused",
    "difficulty": "advanced"
  }'
```

**Response includes**:

- NEET importance rating
- Common question patterns
- High-yield facts (10-15 points)
- Must-know for exam
- Quick revision strategy
- Common mistakes to avoid
- Previous year insights
- Time management tips
- Scoring strategy

---

## 🎯 Specialized Endpoints

### Generate Personalized Study Plan

```bash
curl -X POST http://localhost:8080/study-plan \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Cardiovascular System",
    "time_available": "2 weeks",
    "current_level": "intermediate"
  }'
```

**Response includes**:

- Complete timeline (Phase 1-4)
- Daily routine
- Resources to use
- Milestones and checkpoints
- Spaced repetition schedule
- Motivation boosters

---

### Explain with Analogy

```bash
curl -X POST http://localhost:8080/analogy \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Kidney filtration mechanism"
  }'
```

**Response includes**:

- The analogy (relatable real-world system)
- The mapping (concept ↔ analogy)
- The story (narrative)
- Limitations of the analogy
- Actual medical concept
- Takeaway

---

### Get Learning Recommendations

```bash
curl -X POST http://localhost:8080/learning-recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Pharmacology of beta blockers",
    "user_level": "beginner"
  }'
```

**Response includes**:

- Recommended primary mode
- Supplementary modes
- Practice recommendations
- Complete learning path

---

## 🔬 Basic Endpoints (Original System)

### Ask a Question (Auto-Routing)

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the branches of the facial nerve?"
  }'
```

AI automatically routes to the best specialist (Anatomy in this case).

---

### Ask Specific Specialist

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain glycolysis pathway",
    "agent": "biochemistry"
  }'
```

---

### Collaborative Response (Multiple Experts)

```bash
curl -X POST http://localhost:8080/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the pathophysiology and management of diabetes mellitus"
  }'
```

Gets input from multiple specialists and coordinates their responses.

---

### Get RAG Context

```bash
curl -X POST http://localhost:8080/rag/context \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Loop of Henle function",
    "max_tokens": 1000
  }'
```

See the actual knowledge base context being used.

---

### Search Knowledge Base

```bash
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "hemoglobin oxygen binding",
    "topic": "Human Physiology",
    "limit": 5
  }'
```

---

### Get Knowledge Base Statistics

```bash
curl http://localhost:8080/knowledge/stats
```

**Response**:

```json
{
  "knowledge_base_statistics": {
    "total_chunks": 450,
    "topics": [
      "Human Anatomy",
      "Human Physiology",
      "Medical Biochemistry",
      "Medical Pathology",
      "Medical Pharmacology"
    ],
    "sources": [
      "anatomy.txt",
      "physiology.txt",
      "biochemistry.txt",
      "pathology.txt",
      "pharmacology.txt"
    ],
    "avg_chunk_length": 285.5
  }
}
```

---

### List Available Agents

```bash
curl http://localhost:8080/agents
```

---

### Get All Teaching Modes

```bash
curl http://localhost:8080/teach/modes
```

---

## 📝 Python Examples

### Using requests library:

```python
import requests
import json

BASE_URL = "http://localhost:8080"

# Example 1: Get clinical case
def get_clinical_case(topic):
    response = requests.post(
        f"{BASE_URL}/clinical-case",
        json={"topic": topic}
    )
    return response.json()

# Example 2: Generate quiz
def generate_quiz(topic, difficulty="intermediate"):
    response = requests.post(
        f"{BASE_URL}/quiz",
        json={
            "topic": topic,
            "difficulty": difficulty
        }
    )
    return response.json()

# Example 3: Teach with specific mode
def teach(question, mode="explain", agent=None):
    data = {
        "question": question,
        "mode": mode
    }
    if agent:
        data["agent"] = agent

    response = requests.post(
        f"{BASE_URL}/teach",
        json=data
    )
    return response.json()

# Example 4: Create study plan
def create_study_plan(topic, time_available, current_level):
    response = requests.post(
        f"{BASE_URL}/study-plan",
        json={
            "topic": topic,
            "time_available": time_available,
            "current_level": current_level
        }
    )
    return response.json()

# Usage
if __name__ == "__main__":
    # Get a clinical case
    case = get_clinical_case("Pneumonia")
    print(json.dumps(case, indent=2))

    # Generate quiz
    quiz = generate_quiz("Cardiac cycle", "advanced")
    print(json.dumps(quiz, indent=2))

    # Teach with mnemonic
    mnemonic = teach("Cranial nerves", mode="mnemonic")
    print(json.dumps(mnemonic, indent=2))

    # Create study plan
    plan = create_study_plan(
        "Renal physiology",
        "1 week",
        "intermediate"
    )
    print(json.dumps(plan, indent=2))
```

---

## 🧪 Testing Workflow

### Complete Learning Session Example:

```bash
# 1. Start with learning recommendation
curl -X POST http://localhost:8080/learning-recommendation \
  -H "Content-Type: application/json" \
  -d '{"topic": "Myocardial infarction", "user_level": "intermediate"}'

# 2. Get comprehensive explanation
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{"question": "Pathophysiology of MI", "mode": "explain"}'

# 3. Apply to clinical case
curl -X POST http://localhost:8080/clinical-case \
  -H "Content-Type: application/json" \
  -d '{"topic": "Myocardial infarction"}'

# 4. Generate mnemonics for key facts
curl -X POST http://localhost:8080/mnemonic \
  -H "Content-Type: application/json" \
  -d '{"topic": "Signs and symptoms of MI"}'

# 5. Test knowledge with quiz
curl -X POST http://localhost:8080/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "Myocardial infarction", "difficulty": "intermediate"}'

# 6. Get NEET-focused summary
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{"question": "MI", "mode": "neet_focused"}'
```

---

## 🎯 Subject-Specific Examples

### Anatomy

```bash
# Clinical anatomy
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the boundaries and contents of the femoral triangle",
    "mode": "step_by_step",
    "agent": "anatomy"
  }'
```

### Physiology

```bash
# Cardiovascular physiology
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Regulation of blood pressure",
    "mode": "explain",
    "agent": "physiology"
  }'
```

### Biochemistry

```bash
# Metabolic pathways
curl -X POST http://localhost:8080/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "TCA cycle",
    "difficulty": "advanced",
    "agent": "biochemistry"
  }'
```

### Pathology

```bash
# Disease mechanisms
curl -X POST http://localhost:8080/differential \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Progressive jaundice with weight loss",
    "agent": "pathology"
  }'
```

### Pharmacology

```bash
# Drug mechanisms
curl -X POST http://localhost:8080/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Beta blockers mechanism and clinical uses",
    "mode": "neet_focused",
    "agent": "pharmacology"
  }'
```

---

## 🔄 Before First Use

### Rebuild Knowledge Base (Important!)

```bash
cd d:\Edu-tec\medical_agents_project
python rebuild_knowledge_base.py
```

This rebuilds the FAISS index with all the expanded medical content.

---

## 💡 Pro Tips

1. **Start with explain mode** to understand a new topic
2. **Use socratic mode** for deep understanding
3. **Practice with clinical cases** to apply knowledge
4. **Generate mnemonics** for memorization
5. **Test with quiz mode** before exams
6. **Use neet_focused** for high-yield revision
7. **Create study plans** for systematic preparation
8. **Use step_by_step** for difficult topics
9. **Practice differential diagnosis** for clinical reasoning
10. **Use analogies** to make complex topics memorable

---

## 📊 Expected Response Times

- Simple explain: 5-10 seconds
- Clinical case generation: 10-15 seconds
- Quiz generation (5 questions): 15-20 seconds
- Study plan: 10-15 seconds
- Mnemonic: 5-10 seconds

---

## 🐛 Troubleshooting

### Knowledge base not found?

```bash
python rebuild_knowledge_base.py
```

### Empty responses?

Check your GEMINI_API_KEY in .env file

### Import errors?

```bash
pip install -r requirements.txt
```

### Server not starting?

Check if port 8080 is already in use

---

## 🎓 Success!

Your world-class medical learning AI is ready to help students ace NEET and become confident medical professionals! 🚀

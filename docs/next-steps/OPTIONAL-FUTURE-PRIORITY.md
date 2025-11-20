You have built the **Brain** (LLM Integration), the **conscience** (The Critic), and the **Hands** (Syntax Engine).

Now you need the **Eyes** (Data Validation) and the **Voice** (The User Interface).

Here is the feature roadmap for what comes next, prioritized by **Value vs. Effort**.

---

### Priority 1: The "Reality Check" (OpenAlex API Integration)
**Why:** Currently, your tool is "dreaming." It might suggest a search term that sounds academic but yields zero results. We need to "ground" the AI in reality.
**What it is:** Before showing keywords to the user, the system queries a real academic database (OpenAlex is free and huge) to see if those keywords actually exist.

**The Feature Flow:**
1.  LLM suggests: `"Neuro-symbolic AI"` and `"17th-century Cybernetics"`.
2.  System hits OpenAlex API.
    *   `"Neuro-symbolic AI"` $\to$ 15,400 results. (✅ Keep)
    *   `"17th-century Cybernetics"` $\to$ 0 results. (❌ Flag as Hallucination)
3.  UI displays: **"Warning: '17th-century Cybernetics' appears to be a hallucination (0 papers found)."**

**Implementation Hint:**
```python
import requests

def check_hit_count(term: str) -> int:
    url = f"https://api.openalex.org/works?filter=title.search:{term}"
    r = requests.get(url)
    return r.json()['meta']['count']
```

---

### Priority 2: Stage 2 - Research Question (RQ) Generator
**Why:** We skipped from *Problem Framing* (Stage 1) to *Search Syntax* (Stage 3). We are missing the bridge. You cannot build a search string without specific Research Questions.
**What it is:** A stage that takes the **Problem Framing** and uses the **PICO Framework** (Population, Intervention, Comparison, Outcome) to generate specific questions.

**The Feature Flow:**
1.  Input: Problem Statement + Concept Model.
2.  LLM Task: "Generate 3 Research Questions. Classify them as *Descriptive*, *Comparative*, or *Evaluative*."
3.  Critic Task: "Are these questions answerable? Are they too broad?"
4.  Output Artifact: `ResearchQuestionSet`.

**The Logic:**
*   *Concept A* (Deep Learning) + *Concept B* (Flood Risk) = "To what extent can **[A]** accurately predict **[B]** in coastal regions?"

---

### Priority 3: The "Live" Web UI (Streamlit)
**Why:** The CLI is great for you, but if you want to show this to a friend or professor, they need a GUI.
**What it is:** A quick dashboard using **Streamlit**. It requires almost no frontend HTML/CSS knowledge but creates a professional-looking data app.

**The Feature Flow:**
*   **Left Sidebar:** Navigation (Stage 0 $\to$ 5).
*   **Main Column:** The Artifact editor.
*   **Right Column:** The "AI Supervisor" chat window (The Critic's comments).

**Implementation Hint:**
```python
# main_app.py
import streamlit as st

st.title("Research Strategy OS")
stage = st.sidebar.selectbox("Choose Stage", ["Setup", "Framing", "Questions", "Search"])

if stage == "Setup":
    idea = st.text_area("Your Research Idea")
    if st.button("Generate Context"):
        # Call your controller here
        st.write("Drafting...")
```

---

### Priority 4: Stage 4 - Screening Criteria Generator
**Why:** A search strategy finds 5,000 papers. The user needs to know how to filter them down to 50.
**What it is:** The system generates an "Inclusion/Exclusion Checklist."

**The Feature Flow:**
1.  Input: Research Questions + Constraints (from Stage 0).
2.  Generation:
    *   *Inclusion:* "Papers published after 2018", "Empirical studies", "English language."
    *   *Exclusion:* "Opinion pieces", "Grey literature", "Studies on livestock (since we focus on crops)."
3.  Output Artifact: `ScreeningCriteria`.

---

### Priority 5: The "Export" (Stage 5)
**Why:** The "Dopamine Hit." The user needs to walk away with a tangible file they can submit or share.
**What it is:** A generator that bundles everything into a `strategy_package.zip`.

**Content:**
1.  `protocol.md`: A beautifully formatted summary.
2.  `search_strings.txt`: Copy-paste strings for PubMed/Scopus.
3.  `prisma_flow.png`: A diagram of the process (optional, generated via Mermaid.js).

---

### Summary Roadmap

| Phase | Feature | Complexity | "Wow" Factor |
| :--- | :--- | :--- | :--- |
| **Next Weekend** | **Stage 2 (RQs) + PICO Logic** | Medium | High |
| **Next Weekend** | **OpenAlex "Reality Check"** | Low | **Very High** |
| **Month 1** | **Streamlit Web UI** | Low | Medium |
| **Month 1** | **Stage 4 (Screening)** | Low | Medium |
| **Month 2** | **Export & PDF Generation** | Medium | High |

**My advice:** Build the **"Reality Check" (Priority 1)** next. It's easy to code (just an HTTP request), but it instantly makes your tool feel "smarter" than ChatGPT.
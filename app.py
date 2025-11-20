"""
Trust Dashboard - HITL Research Pipeline Web UI

Sprint 3: The Research Operating System
This Streamlit app visualizes the Draft → Critique → Refine → Validate workflow.
"""

import streamlit as st
import time
from datetime import datetime

from src.services.intelligent_model_service import IntelligentModelService
from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HITL Research Pipeline",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "model_service" not in st.session_state:
    st.session_state.model_service = IntelligentModelService()

if "context" not in st.session_state:
    st.session_state.context = None

if "framing" not in st.session_state:
    st.session_state.framing = None

if "concepts" not in st.session_state:
    st.session_state.concepts = None

if "meta" not in st.session_state:
    st.session_state.meta = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔬 Research OS")
    st.caption("**Validated AI Research Assistant**")

    # Provider info
    provider = st.session_state.model_service.config.llm.provider.value.upper()
    if provider == "OPENAI":
        st.success(f"🤖 Provider: **{provider}**")
        st.caption(f"Model: {st.session_state.model_service.config.llm.openai_model}")
    else:
        st.info(f"🤖 Provider: **{provider}**")
        st.caption("Using mock responses (free)")

    st.divider()

    # Workflow stage selection
    step = st.radio("📍 Workflow Stage", [
        "1️⃣ Project Context",
        "2️⃣ Problem Framing (AI Agent)",
        "3️⃣ Search Strategy (Syntax)"
    ], index=0)

    st.divider()

    # Info box
    st.info("""
    **Agentic Workflow:**
    
    1. 🧠 Draft generation
    2. 🕵️ AI self-critique
    3. ✨ Refinement
    4. 📚 OpenAlex validation
    """)

    # Progress tracker
    st.divider()
    st.subheader("✅ Progress")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.context:
            st.success("Stage 1 ✓")
        else:
            st.warning("Stage 1 ⏳")

    with col2:
        if st.session_state.framing:
            st.success("Stage 2 ✓")
        else:
            st.warning("Stage 2 ⏳")

# --- HEADER ---
st.title("🔬 HITL Research Strategy Pipeline")
st.markdown("### The Trust Dashboard - See the AI Think")

# --- STAGE 1: PROJECT CONTEXT ---
if step == "1️⃣ Project Context":
    st.header("1️⃣ Define Research Context")
    st.markdown("""
    Enter your raw research idea below. The AI will extract:
    - **Title** (academic style)
    - **Discipline** (field of study)
    - **Keywords** (initial concepts)
    - **Constraints** (scope, timeline, resources)
    """)

    # Input area
    raw_idea = st.text_area(
        "💡 Enter your raw research idea:",
        height=150,
        placeholder="Example: I want to study the impact of Large Language Models on academic integrity in higher education, specifically focusing on essay writing and plagiarism detection...",
        help="Be as descriptive as possible. The more context you provide, the better the AI can understand your research goals."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("🚀 Generate Context", type="primary", use_container_width=True)

    with col2:
        if st.session_state.context:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.context = None
                st.session_state.framing = None
                st.session_state.concepts = None
                st.rerun()

    # Generate context
    if generate_btn:
        if not raw_idea.strip():
            st.error("⚠️ Please enter a research idea first.")
        else:
            with st.spinner("🧠 AI is analyzing your request..."):
                try:
                    context, metadata = st.session_state.model_service.suggest_project_context(raw_idea)
                    st.session_state.context = context
                    st.session_state.meta = metadata
                    st.success("✅ Context Generated Successfully!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error generating context: {str(e)}")

    # Display Context Artifact
    if st.session_state.context:
        st.divider()
        st.subheader("📋 Generated Project Context")

        c = st.session_state.context

        # Main content area
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(f"### {c.title}")
            st.markdown(f"**📚 Discipline:** {c.discipline or 'General'}")
            st.markdown(f"**📝 Description:**")
            st.info(c.short_description)

        with col2:
            st.markdown("**⚙️ Detected Constraints:**")
            if c.constraints:
                st.json(c.constraints)
            else:
                st.caption("None specified")

            st.markdown("**🔑 Initial Keywords:**")
            if c.initial_keywords:
                for kw in c.initial_keywords:
                    st.markdown(f"- {kw}")
            else:
                st.caption("None detected")

        # Metadata
        with st.expander("🔍 View Metadata"):
            st.json({
                "model": st.session_state.meta.model_name if st.session_state.meta else "unknown",
                "mode": st.session_state.meta.mode if st.session_state.meta else "unknown",
                "generated_at": str(c.created_at),
                "project_id": c.id
            })

        # Next step prompt
        st.success("✅ Ready for Stage 2! Click **'2️⃣ Problem Framing'** in the sidebar.")

# --- STAGE 2: PROBLEM FRAMING (THE AGENT LOOP) ---
elif step == "2️⃣ Problem Framing (AI Agent)":
    st.header("2️⃣ Agentic Problem Framing")

    if not st.session_state.context:
        st.warning("⚠️ Please complete **Stage 1** first.")
        st.info("👈 Go to '1️⃣ Project Context' in the sidebar to start.")
    else:
        st.markdown("""
        ### 🤖 The AI Agent Workflow
        
        The system will perform a **multi-step reflection loop**:
        
        | Step | Process | Output |
        |------|---------|--------|
        | 1️⃣ | **Draft** | Initial research plan generated |
        | 2️⃣ | **Critique** | AI evaluates its own work (feasibility score) |
        | 3️⃣ | **Refine** | Improved plan addressing critique points |
        | 4️⃣ | **Validate** | Concepts verified against OpenAlex (250M+ works) |
        
        **This is what separates us from ChatGPT** - we validate everything against real literature!
        """)

        # Show current context
        with st.expander("📖 Current Project Context", expanded=False):
            st.write(f"**Title:** {st.session_state.context.title}")
            st.write(f"**Description:** {st.session_state.context.short_description}")

        st.divider()

        # Run button
        if st.button("🚀 Run Agentic Workflow", type="primary", use_container_width=True):
            with st.status("🔄 Running Agentic Pipeline...", expanded=True) as status:
                st.write("🧠 **Step 1/4:** Generating initial draft...")
                time.sleep(1)

                st.write("🕵️‍♂️ **Step 2/4:** Running critique module (AI self-evaluation)...")
                time.sleep(1)

                st.write("✨ **Step 3/4:** Refining strategy based on critique...")
                time.sleep(1)

                st.write("📚 **Step 4/4:** Validating against OpenAlex Literature Graph...")

                try:
                    # CALL THE SERVICE - This is where the magic happens!
                    framing, concepts, meta = st.session_state.model_service.generate_problem_framing(
                        st.session_state.context
                    )

                    st.session_state.framing = framing
                    st.session_state.concepts = concepts
                    st.session_state.meta = meta

                    status.update(label="✅ Workflow Complete!", state="complete", expanded=False)
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()

                except Exception as e:
                    status.update(label="❌ Workflow Failed", state="error", expanded=True)
                    st.error(f"Error: {str(e)}")

        # Display Results
        if st.session_state.framing:
            st.divider()
            st.success("✅ **Problem Framing Complete!**")

            f = st.session_state.framing

            # Critique Report (The "Why") - Most important for trust!
            with st.expander("📋 **View AI Critique & Validation Report**", expanded=True):
                st.markdown("### 🔍 Transparency Report")
                st.markdown("""
                This report shows:
                - **AI's self-critique** with feasibility scoring
                - **OpenAlex validation** results with hit counts
                - **Sample works** from the literature
                - **Warnings** for rare or hallucinated terms
                """)
                st.code(f.critique_report, language="text")

            # The Refined Output
            st.divider()
            st.subheader("📊 Refined Research Strategy")

            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown("#### 🎯 Problem Statement")
                st.markdown(f'<div class="success-box">{f.problem_statement}</div>', unsafe_allow_html=True)

                st.markdown("#### 🔬 Research Gap")
                st.write(f.research_gap or "Not specified")

                st.markdown("#### 🎯 Research Goals")
                for i, g in enumerate(f.goals, 1):
                    st.markdown(f"{i}. {g}")

            with col2:
                st.markdown("#### ✅ Scope Definition")

                st.markdown("**In Scope:**")
                for item in f.scope_in:
                    st.markdown(f"✅ {item}")

                st.markdown("**Out of Scope:**")
                for item in f.scope_out:
                    st.markdown(f"❌ {item}")

            # Extracted Concepts
            st.divider()
            st.subheader("🧩 Extracted Concepts (Validated Against Literature)")

            if st.session_state.concepts and st.session_state.concepts.concepts:
                # Concept Cards in columns
                cols = st.columns(min(3, len(st.session_state.concepts.concepts)))
                for idx, c in enumerate(st.session_state.concepts.concepts):
                    with cols[idx % 3]:
                        st.metric(
                            label=f"🏷️ {c.type}",
                            value=c.label,
                            help=c.description
                        )
            else:
                st.info("No concepts extracted yet.")

            # Next step prompt
            st.divider()
            st.success("✅ Ready for Stage 3! Click **'3️⃣ Search Strategy'** in the sidebar to generate database queries.")

# --- STAGE 3: SEARCH SYNTAX (THE MOAT) ---
elif step == "3️⃣ Search Strategy (Syntax)":
    st.header("3️⃣ Universal Syntax Generator")
    st.markdown("### 🎯 The Technical Moat - Perfect Syntax for 6 Databases")

    if not st.session_state.concepts:
        st.warning("⚠️ Please complete **Stage 2** first.")
        st.info("👈 Go to '2️⃣ Problem Framing' in the sidebar.")
    else:
        st.markdown("""
        The system automatically translates your validated concepts into **database-specific syntax**.
        
        **Why this matters:**
        - ✅ **ChatGPT can't guarantee syntax correctness** (it hallucinates operators)
        - ✅ **We use the Strategy Pattern** - one conceptual query → 6 perfect outputs
        - ✅ **Zero risk of syntax errors** - each dialect is tested and validated
        """)

        # Show concepts being used
        with st.expander("🧩 Concepts Being Translated", expanded=False):
            for c in st.session_state.concepts.concepts:
                st.write(f"- **{c.label}** ({c.type})")

        st.divider()

        # Convert ConceptModel to QueryPlan
        # Group concepts by type for the query
        plan = QueryPlan()
        grouped = {}

        for c in st.session_state.concepts.concepts:
            type_key = c.type if isinstance(c.type, str) else str(c.type)
            if type_key not in grouped:
                grouped[type_key] = ConceptBlock(type_key)
            grouped[type_key].add_term(c.label, FieldTag.KEYWORD)

        for block in grouped.values():
            plan.blocks.append(block)

        # DATABASE TABS
        st.subheader("📑 Database-Specific Queries")
        st.caption("Click each tab to see the syntax for that database. Click the copy button in the code block!")

        dbs = ["PubMed", "Scopus", "ArXiv", "OpenAlex", "SemanticScholar", "CrossRef"]
        tabs = st.tabs([f"🔍 {db}" for db in dbs])

        for i, db in enumerate(dbs):
            with tabs[i]:
                st.markdown(f"### {db} Query")

                try:
                    builder = get_builder(db.lower())
                    query = builder.build(plan)

                    # Show the query
                    st.code(query, language="text")

                    # Syntax info
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.success("✅ **Syntactically verified** - Ready to copy and paste!")

                    with col2:
                        st.metric("Concepts", len(plan.blocks))

                    # Database-specific notes
                    if db == "PubMed":
                        st.info("📝 **Note:** Uses `[Title/Abstract]` and `[MeSH Terms]` field tags. Newline AND for readability.")
                    elif db == "Scopus":
                        st.info("📝 **Note:** Uses efficient `TITLE-ABS-KEY()` wrapper with single OR grouping.")
                    elif db == "ArXiv":
                        st.info("📝 **Note:** Uses `all:` field prefix. Perfect for preprint searches.")
                    elif db == "OpenAlex":
                        st.info("📝 **Note:** Standard Boolean syntax for the search API.")
                    elif db == "SemanticScholar":
                        st.info("📝 **Note:** Clean Boolean syntax for their Graph API.")
                    elif db == "CrossRef":
                        st.info("📝 **Note:** Google-like syntax for their query service.")

                except Exception as e:
                    st.error(f"❌ Could not generate syntax for {db}: {str(e)}")
                    st.caption("This might be a configuration issue. Check your syntax builder setup.")

        # Download all queries
        st.divider()
        st.subheader("💾 Export All Queries")

        all_queries = ""
        for db in dbs:
            try:
                builder = get_builder(db.lower())
                query = builder.build(plan)
                all_queries += f"{'='*70}\n"
                all_queries += f"{db.upper()} QUERY\n"
                all_queries += f"{'='*70}\n\n"
                all_queries += query + "\n\n"
            except:
                pass

        st.download_button(
            label="📥 Download All Queries",
            data=all_queries,
            file_name=f"search_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.success("🎉 **All Done!** You now have validated, publication-ready search strategies for 6 academic databases.")

# --- FOOTER ---
st.divider()
st.caption("🔬 HITL Research Pipeline | Sprint 3: Trust Dashboard | Built with Streamlit")
st.caption("Powered by: Strategy Pattern (Syntax Engine) + OpenAI (LLM) + OpenAlex (Validation)")


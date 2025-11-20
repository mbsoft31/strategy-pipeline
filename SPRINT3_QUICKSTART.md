# Sprint 3: Trust Dashboard - Quick Start Guide

## 🚀 Launch in 30 Seconds

### Step 1: Ensure Dependencies
```bash
# Streamlit should already be installed
pip install streamlit>=1.30.0
```

### Step 2: Launch Dashboard
```bash
streamlit run app.py
```

### Step 3: Open Browser
The dashboard automatically opens at: **http://localhost:8501**

---

## 📖 User Guide

### Stage 1: Project Context

1. **Enter Your Research Idea**
   ```
   Example: "I want to study the impact of AI-generated 
   content on academic integrity in university essays"
   ```

2. **Click "Generate Context"**
   - Wait 2-5 seconds
   - See AI-extracted title, keywords, discipline

3. **Review Results**
   - Check if keywords match your intent
   - View detected constraints
   - Expand metadata for details

### Stage 2: Problem Framing (The Magic!)

1. **Click "Run Agentic Workflow"**
   - Watch the 4-step process:
     - 🧠 Draft generation
     - 🕵️ AI critique
     - ✨ Refinement
     - 📚 OpenAlex validation

2. **Open Critique Report** (Most Important!)
   - See AI's feasibility score (1-10)
   - Read specific critique points
   - **Check OpenAlex validation:**
     - ✅ Green = Validated (1000+ works)
     - ⚠️ Yellow = Rare (<100 works)
     - ❌ Red = Hallucination (0 works)

3. **Review Refined Strategy**
   - Problem statement
   - Research gap
   - Goals (3-5 specific objectives)
   - Scope IN/OUT

4. **View Extracted Concepts**
   - See concept cards with types
   - These feed into syntax generation

### Stage 3: Search Strategy

1. **Click Through Database Tabs**
   - PubMed (medical literature)
   - Scopus (multidisciplinary)
   - arXiv (preprints)
   - OpenAlex (open access)
   - Semantic Scholar (AI-powered)
   - CrossRef (citations)

2. **Copy Query Syntax**
   - Click the copy button in code block
   - Paste directly into database search

3. **Download All Queries**
   - Click "Download All Queries" button
   - Get text file with all 6 queries
   - Use for documentation/reproducibility

---

## 💡 Tips & Tricks

### Get Better Results

**Be Specific in Your Idea:**
```
❌ Bad:  "Study AI in education"
✅ Good: "Investigate GPT-4's impact on essay plagiarism 
         detection in undergraduate computer science courses"
```

**Review the Critique:**
- The AI's self-critique is gold!
- It often catches scope issues you missed
- Trust the feasibility score

**Check Validation:**
- 0 hits = Term doesn't exist (hallucination)
- Low hits (<100) = Verify spelling/terminology
- High hits (1000+) = Well-established concept

### Navigation

- Use **sidebar radio buttons** to jump between stages
- **Progress tracker** shows completed stages
- Can go back and regenerate at any stage

### Provider Modes

**Mock Mode** (Free testing):
```env
LLM__PROVIDER=mock
```
- Instant responses
- Realistic mock data
- Great for demos

**OpenAI Mode** (Production):
```env
LLM__PROVIDER=openai
LLM__OPENAI_API_KEY=sk-proj-xxxxx
```
- Real AI intelligence
- Actual OpenAlex validation
- ~$0.006 per project

---

## 🐛 Troubleshooting

### Dashboard Won't Start

**Error: "streamlit: command not found"**
```bash
pip install streamlit
```

**Error: Port already in use**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### API Issues

**Error: "OpenAI API key not found"**
```bash
# Check .env file
cat .env | grep OPENAI

# Or use Mock mode
# Set LLM__PROVIDER=mock in .env
```

**OpenAlex timeout:**
- Check internet connection
- Validation service retries automatically
- Increase timeout in config if needed

### Display Issues

**UI looks broken:**
- Try hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
- Clear Streamlit cache: Click "⋮" menu → "Clear cache"

**Session state lost:**
- Don't refresh page during workflow
- Complete each stage before moving on
- Use "Start Over" button to reset

---

## 📊 What to Expect

### Timing

- **Stage 1 (Context):** 2-5 seconds (Mock) or 5-10 seconds (OpenAI)
- **Stage 2 (Framing):** 5-10 seconds (Mock) or 20-40 seconds (OpenAI)
- **Stage 3 (Syntax):** Instant

### Costs (OpenAI Mode)

- Stage 1: ~$0.001
- Stage 2: ~$0.005 (includes validation)
- Stage 3: $0 (local generation)
- **Total: ~$0.006 per complete workflow**

### Output Quality

**Mock Mode:**
- Realistic but generic responses
- Perfect for UI testing
- Concept validation is simulated

**OpenAI Mode:**
- High-quality, context-aware responses
- Real critique with insights
- Actual OpenAlex validation with hit counts

---

## 🎯 Example Workflows

### Example 1: Medical Research

**Input:**
```
Evaluate effectiveness of mindfulness meditation apps 
for reducing anxiety in college students
```

**Expected Output:**
- Title: "Mobile Mindfulness Interventions for College Student Anxiety"
- Keywords: mindfulness, meditation apps, anxiety, college students, mental health
- Concepts: Population (college students), Intervention (mindfulness apps), Outcome (anxiety reduction)
- Validation: All terms validated with 1000+ works

### Example 2: Computer Science

**Input:**
```
Compare performance of transformer models versus 
CNNs for medical image classification
```

**Expected Output:**
- Title: "Transformer vs. CNN Performance in Medical Imaging"
- Keywords: transformers, CNNs, medical imaging, classification
- Concepts: Method (transformers, CNNs), Application (medical imaging), Metric (classification accuracy)
- Validation: All validated

### Example 3: Social Sciences

**Input:**
```
Examine social media's impact on political polarization 
among Generation Z voters
```

**Expected Output:**
- Title: "Social Media Effects on Gen Z Political Polarization"
- Keywords: social media, political polarization, Generation Z, voting behavior
- Concepts: Population (Gen Z), Exposure (social media), Outcome (polarization)
- Validation: Most validated, some warnings for emerging terms

---

## 🎓 Best Practices

### 1. Iterate on Context
- Don't accept first generation if keywords are off
- Click "Start Over" and rephrase idea
- More detail = better results

### 2. Read the Critique
- The AI often catches issues you missed
- Low feasibility score? Narrow your scope
- Critique says "too broad"? Be more specific

### 3. Verify Validation
- Check hit counts carefully
- 0 hits = Rephrase that term
- <100 hits = Double-check spelling
- 1000+ hits = Good to go!

### 4. Use All Databases
- Different databases, different coverage
- PubMed for medical
- arXiv for CS/physics preprints
- Scopus for multidisciplinary

### 5. Export Everything
- Download queries for reproducibility
- Screenshot critique report
- Document your workflow

---

## 🚀 Advanced Features

### Session State

The dashboard remembers your progress:
- Navigate freely between stages
- Come back to review results
- Only lost on page refresh

### Keyboard Shortcuts

- `R` - Rerun app (when in Streamlit interface)
- `Ctrl+Enter` - Submit text area
- `Tab` - Navigate between fields

### URL Parameters (Future)

Share workflows with URL:
```
http://localhost:8501/?project=diabetes-telemedicine
```
(Not yet implemented - Sprint 4!)

---

## 📝 Reporting Issues

If something doesn't work:

1. Check browser console (F12)
2. Check terminal output where Streamlit is running
3. Try different browser (Chrome recommended)
4. Clear cache: "⋮" menu → "Clear cache"

---

## 🎉 You're Ready!

The Trust Dashboard is your **Research Operating System**.

**Start with a simple query** to get familiar:
```
Effect of exercise on depression in older adults
```

Then **try your actual research question**.

**Happy researching!** 🔬


# Frontend Specification for Strategy Pipeline

**Project:** Strategy Pipeline - Intelligent SLR Automation  
**Target Users:** Academic researchers, research librarians, R&D strategists  
**Prepared:** November 22, 2025  
**Status:** Ready for Implementation

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [User Experience Goals](#user-experience-goals)
3. [Tech Stack Recommendations](#tech-stack-recommendations)
4. [Architecture Overview](#architecture-overview)
5. [Feature Requirements](#feature-requirements)
6. [Deliverables Checklist](#deliverables-checklist)
7. [Additional Resources](#additional-resources)

---

## 🎯 Project Overview

### What is Strategy Pipeline?

An intelligent, human-in-the-loop (HITL) platform for automating systematic literature review (SLR) strategy development. The system guides researchers from a raw idea through 7 structured stages to produce validated, multi-database Boolean search queries with guaranteed syntax correctness.

### Core Value Proposition

- **Anti-Hallucination Query Engine:** Guarantees 100% valid Boolean syntax (no NEAR/ADJ/PROX hallucinations)
- **Multi-Database Support:** 7 scholarly databases (PubMed, Scopus, arXiv, OpenAlex, etc.)
- **Human-in-the-Loop:** Approval checkpoints at every stage with editable drafts
- **Reproducibility:** All artifacts saved as JSON with full audit trail
- **LLM-Assisted:** Optional AI help for brainstorming while maintaining deterministic validation

### Primary Users

| User Type | Primary Goal | Pain Points Frontend Should Solve |
|-----------|--------------|-----------------------------------|
| Academic Researcher | Build SLR protocol fast | Complex query syntax, database-specific rules |
| Research Librarian | Multi-database query assembly | Time-consuming manual construction |
| R&D Strategist | Landscape scanning | Lack of structured exploration framework |
| Applied AI Scientist | Emerging topic mapping | Non-reproducible ad-hoc searches |

---

## ✨ User Experience Goals

### 1. **Progressive Disclosure**
- Start simple (raw idea input)
- Reveal complexity gradually through stages
- Hide advanced options behind expandable sections

### 2. **Trust & Transparency**
- Show what the AI did and why
- Clear diff/preview before approvals
- Validation feedback in plain language

### 3. **Guidance & Education**
- Tooltips explaining PICO, Boolean operators, complexity levels
- Examples and templates accessible contextually
- Inline help without leaving workflow

### 4. **Efficiency**
- Keyboard shortcuts for common actions
- Bulk edit capabilities (e.g., concept terms)
- Save drafts automatically
- Quick navigation between stages

### 5. **Professional Output**
- Clean, export-ready artifacts
- Printable/shareable strategy summaries
- Citation-ready format

---

## 🛠 Tech Stack Recommendations (Stack-Agnostic)

Choose a stack that fits your team's expertise. Below are options with pros/cons:

### Frontend Framework

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **React** | Rich ecosystem, component reuse | Steeper learning curve | Complex interactive UIs |
| **Vue.js** | Gentler learning curve, good DX | Smaller ecosystem than React | Rapid prototyping |
| **Svelte** | Minimal bundle size, reactive | Smaller community | Performance-critical apps |
| **Alpine.js + HTMX** | Minimal JS, server-driven | Less suitable for SPAs | Simple, fast iterations |

**Recommendation:** React or Vue.js for rich interactivity; HTMX if leveraging existing Flask backend.

### State Management

| Option | Use Case |
|--------|----------|
| **Context API** (React) | Small-medium apps |
| **Pinia** (Vue) | Vue projects |
| **Zustand / Jotai** (React) | Lightweight state |
| **Redux Toolkit** | Complex state with time-travel debugging |

**Recommendation:** Start simple (Context API / Pinia); upgrade to Redux Toolkit if state becomes unwieldy.

### UI Component Library

| Option | Strengths | Framework |
|--------|-----------|-----------|
| **shadcn/ui** | Customizable, accessible, modern | React |
| **Ant Design** | Enterprise-ready, comprehensive | React / Vue |
| **Vuetify** | Material Design, rich components | Vue |
| **Headless UI** | Unstyled, full control | React / Vue |
| **DaisyUI + Tailwind** | Rapid styling, opinionated | Any |

**Recommendation:** shadcn/ui (React) or Vuetify (Vue) for speed + quality.

### Styling

| Option | Approach |
|--------|----------|
| **Tailwind CSS** | Utility-first (recommended for flexibility) |
| **CSS Modules** | Scoped styles, traditional CSS |
| **Styled Components** | CSS-in-JS (React) |
| **SCSS** | Traditional preprocessing |

**Recommendation:** Tailwind CSS for rapid iteration and consistency.

### API Communication

- **Fetch API** (native)
- **Axios** (popular library)
- **TanStack Query (React Query)** (caching + state management)
- **SWR** (lightweight React hooks)

**Recommendation:** TanStack Query or SWR for automatic caching and real-time updates.

### Form Handling

- **React Hook Form** (React, performance-optimized)
- **Formik** (React, feature-rich)
- **VeeValidate** (Vue)
- **Native HTML5** (for simple forms)

**Recommendation:** React Hook Form (React) or VeeValidate (Vue).

### Real-Time Updates (Optional)

- **WebSockets** (native)
- **Server-Sent Events (SSE)** (simpler for one-way updates)
- **Polling** (simplest, good enough for HITL workflow)

**Recommendation:** Polling (every 2-5s) for draft status; SSE for LLM streaming.

---

## 🏗 Architecture Overview

### High-Level Flow

```
User Input → Stage Execution (Backend) → Draft Artifact → User Approval → Next Stage
```

### Key Architectural Principles

1. **Backend-Driven Logic:** All business logic (validation, LLM calls, query generation) stays in Python backend
2. **Frontend as View Layer:** Fetch data, render UI, handle user input, submit approvals
3. **RESTful API:** Frontend communicates via HTTP JSON endpoints
4. **Optimistic UI Updates:** Show changes immediately; rollback if server rejects
5. **Modular Stage Components:** Each stage has a reusable React/Vue component

### API Integration Points

See `API_SPECIFICATION.md` for detailed endpoint documentation.

**Key Endpoints:**
- `POST /api/projects` - Create new project
- `GET /api/projects/:id` - Get project details
- `POST /api/projects/:id/stages/:stage_name` - Execute stage
- `PUT /api/projects/:id/artifacts/:artifact_type` - Approve/edit artifact
- `GET /api/projects/:id/artifacts/:artifact_type` - Fetch artifact

### Data Flow Example (Stage Execution)

```
1. User clicks "Run Problem Framing"
2. Frontend: POST /api/projects/{id}/stages/problem-framing
3. Backend: Executes stage, returns draft ProblemFraming artifact
4. Frontend: Displays draft in editable form
5. User: Edits goals, adds notes
6. User: Clicks "Approve"
7. Frontend: PUT /api/projects/{id}/artifacts/ProblemFraming (with edits)
8. Backend: Saves approved artifact, updates status
9. Frontend: Unlocks next stage (Research Questions)
```

---

## 📐 Feature Requirements

See individual feature spec documents for details:

- `01_PROJECT_DASHBOARD.md` - Project list, creation, status overview
- `02_STAGE_EXECUTION.md` - Stage progression UI, draft editing, approvals
- `03_ARTIFACT_VIEWER.md` - JSON artifact display, diff viewer, history
- `04_QUERY_BUILDER.md` - Query preview, complexity analysis, export
- `05_SETTINGS.md` - LLM provider config, preferences, export settings

### Priority Levels

| Priority | Features |
|----------|----------|
| **P0 (MVP)** | Project creation, Stage 0-4 execution, Artifact approval, Basic query display |
| **P1 (Launch)** | Stage 5-6, Diff viewer, Export bundle, Syntax highlighting |
| **P2 (Enhancement)** | Real-time streaming, Query dry-run, Multi-project compare |

---

## ✅ Deliverables Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Setup project (framework, build tooling, linting)
- [ ] Implement API client layer
- [ ] Create layout/navigation shell
- [ ] Build project list + creation flow
- [ ] Implement Stage 0 (Project Setup) UI

### Phase 2: Core Pipeline (Week 3-4)
- [ ] Implement Stages 1-4 execution UI
- [ ] Build artifact approval workflow
- [ ] Add draft editing (inline or modal)
- [ ] Display validation errors clearly
- [ ] Implement stage progression logic

### Phase 3: Advanced Features (Week 5-6)
- [ ] Add query syntax highlighting
- [ ] Build complexity analysis visualizations
- [ ] Implement export bundle download
- [ ] Add diff viewer for edits
- [ ] Create settings panel

### Phase 4: Polish (Week 7)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Responsive design testing
- [ ] Error state handling
- [ ] Loading states and skeletons
- [ ] User onboarding tour (optional)

---

## 📚 Additional Resources

### Design Assets
- See `DESIGN_SYSTEM.md` for color palette, typography, spacing
- See `UI_COMPONENTS.md` for component specifications
- See `WIREFRAMES.md` for screen-by-screen mockups

### API Documentation
- See `API_SPECIFICATION.md` for complete endpoint reference
- See `DATA_MODELS.md` for artifact schemas (JSON structures)

### User Flows
- See `USER_FLOWS.md` for step-by-step workflows
- See `ERROR_HANDLING.md` for failure scenarios

### Testing
- See `TESTING_REQUIREMENTS.md` for unit/integration/e2e test specs

---

## 🚀 Getting Started

1. **Read all spec documents** in this folder (start with numbered files 01-05)
2. **Choose your tech stack** based on team expertise
3. **Set up development environment** (API proxy, mock server optional)
4. **Implement MVP features** (P0) first
5. **Iterate with user feedback** before adding P1/P2 features

---

## 🤝 Collaboration Points

### Questions to Resolve with Backend Team
- WebSocket support for real-time updates?
- Pagination for project list (if >100 projects expected)?
- File upload support for bulk import (future)?
- Authentication/authorization flow (if multi-user)?

### Assumptions
- Backend provides RESTful JSON API (documented separately)
- No authentication required for MVP (single-user mode)
- Artifacts are JSON objects matching schemas in `DATA_MODELS.md`
- Deployable as static SPA + separate backend server

---

**Next Step:** Read `01_PROJECT_DASHBOARD.md` to start with the first feature.


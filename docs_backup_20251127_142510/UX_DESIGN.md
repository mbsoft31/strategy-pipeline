"""UX Design Documentation for HITL Research Strategy Pipeline Web UI

This document outlines the key UX principles and design decisions for an optimal user experience.
"""

# Core UX Principles

## 1. Progressive Disclosure
- Show users only what they need at each stage
- Avoid overwhelming with all options upfront
- Guided workflow with clear next steps

Implementation:
- Landing page → simple project creation
- Project detail → clear stage progression
- Each stage → focused on one artifact at a time

## 2. Clear Visual Hierarchy
- Stage progression visualized as a timeline
- Color coding for status (draft/approved/not started)
- Prominent CTAs for next actions

Status colors:
- Green: Approved/completed
- Yellow: Draft/in review
- Gray: Not started
- Blue: Current/active

## 3. Instant Feedback
- HTMX for no-reload interactions
- Toast notifications for success/errors
- Loading indicators during async operations
- Inline validation for forms

## 4. Contextual Help
- AI-generated prompts at each stage
- Example ideas and templates
- Inline tips and guidance
- Expandable help sections

## 5. Efficient Editing
- Auto-save drafts
- Inline editing where possible
- Keyboard shortcuts for power users
- Batch editing for lists (keywords, goals, etc.)

## 6. Mobile-First Responsive
- Tailwind CSS for responsive layouts
- Touch-friendly controls
- Collapsible sections on mobile
- Readable typography at all sizes

# Page-by-Page UX Strategy

## Landing Page (index.html)
Goal: Quick overview + easy project creation

Features:
- Prominent "Start New Project" CTA
- Project cards with status at a glance
- "How it works" visual guide
- Empty state with encouraging message

UX Wins:
- User can start in 1 click
- No login required (for MVP)
- Projects visible immediately
- Clear value proposition

## New Project Page (new_project.html)
Goal: Low-friction project initiation

Features:
- Single large textarea for research idea
- Character counter with generous limit
- Collapsible examples section
- Auto-focus on input field

UX Wins:
- No overwhelming multi-step form
- Examples available but not intrusive
- Progress indication (breadcrumb)
- Helpful placeholder text

## Project Detail Page (project_detail.html)
Goal: Clear status overview + guided next steps

Features:
- Visual stage timeline with completion status
- Expandable stage cards
- Quick actions sidebar
- Artifact summaries in context

UX Wins:
- See entire pipeline at once
- Understand where you are
- Next action always clear
- No dead ends

## Stage Pages (stage-specific)
Goal: Focused editing + easy approval

Features:
- AI-generated suggestions highlighted
- Inline editing with live preview
- Contextual help prompts
- One-click approval

UX Wins:
- Review checklist visible
- Edit without switching modes
- Clear save/approve distinction
- Can return anytime

# Interaction Patterns

## 1. Auto-save vs. Explicit Save
Decision: Explicit "Approve" for stage completion, auto-draft for edits

Rationale:
- Users need control over when stage is "done"
- Drafts prevent data loss
- Approval is intentional action

## 2. Modal vs. Inline Editing
Decision: Inline editing on dedicated pages

Rationale:
- More space for complex forms
- Clearer focus
- Easier to show context/help
- Better mobile experience

## 3. Loading States
Pattern: Optimistic UI with spinners for slow operations

Examples:
- Creating project: Spinner + "Creating project..."
- Running stage: Spinner + "Generating draft..."
- Approving: Brief spinner + toast notification

## 4. Error Handling
Pattern: Inline errors + toast for critical failures

Examples:
- Empty required field: Red border + message below
- Server error: Toast notification + retry button
- Validation: Immediate inline feedback

# Accessibility Considerations

- Semantic HTML (nav, main, article)
- ARIA labels for interactive elements
- Keyboard navigation (tab order)
- Color contrast ratios (WCAG AA)
- Focus indicators
- Screen reader compatible

# Performance Optimizations

- HTMX for partial page updates (faster than full reload)
- Tailwind CDN for rapid prototyping (switch to build for production)
- Alpine.js for lightweight interactivity (3KB gzipped)
- Lazy load stage content
- Paginate long artifact lists

# Future Enhancements

## Phase 2 (Month 2-3)
- Collaborative editing (WebSocket)
- Version history/diff view
- Export to multiple formats
- Keyboard shortcuts panel

## Phase 3 (Month 4-6)
- Dark mode toggle
- Customizable workflows
- AI chat assistant sidebar
- Integration with reference managers

# Testing Strategy

## Usability Tests
- Task: Create project → approve Stage 0 → approve Stage 1
- Metrics: Time to completion, error rate, satisfaction
- Target: <5 min for first two stages

## A/B Tests
- CTA placement (above fold vs. below)
- Stage progression layout (timeline vs. checklist)
- Help text prominence (expandable vs. always visible)

## Accessibility Audit
- Automated: axe-core
- Manual: Screen reader testing (NVDA/JAWS)
- Keyboard-only navigation test

# Design System

## Typography
- Headings: Inter (bold, 2xl → sm)
- Body: Inter (regular, base)
- Code: JetBrains Mono

## Spacing
- Consistent 4px baseline grid
- Section padding: 2rem (8)
- Card padding: 1.5rem (6)
- Element gap: 1rem (4)

## Colors (Tailwind defaults)
- Primary: Blue-600
- Success: Green-600
- Warning: Yellow-400
- Danger: Red-600
- Neutral: Gray-50 to Gray-900

## Components
- Buttons: Rounded-lg, shadow-sm
- Inputs: Border, focus:ring-2
- Cards: White bg, shadow-sm, rounded-lg
- Badges: Rounded-full, px-3 py-1

# Metrics to Track

## Engagement
- Projects created per user
- Stages completed per project
- Time spent per stage
- Return rate (multi-session projects)

## Friction Points
- Form abandonment rate
- Error frequency by field
- Help section expansion rate
- Page exit points

## Success Indicators
- % projects reaching Stage 1
- % projects fully approved
- User satisfaction (NPS)
- Task completion rate

---

This design prioritizes clarity, efficiency, and guidance throughout the research strategy creation process.


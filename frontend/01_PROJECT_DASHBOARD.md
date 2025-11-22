# 01 - Project Dashboard Feature Specification

**Feature:** Project List & Creation Interface  
**Priority:** P0 (MVP)  
**Estimated Complexity:** Medium

---

## 🎯 Purpose

Provide users with an overview of all their research projects and enable quick project creation from a raw idea.

---

## 📐 User Interface Requirements

### 1. Project List View

**Layout:**
```
+----------------------------------------------------------+
| Strategy Pipeline                         [+ New Project]|
+----------------------------------------------------------+
| Search: [___________________]  Filter: [All | Active | …]|
+----------------------------------------------------------+
| Title               | Stage      | Updated    | Actions  |
|---------------------|------------|------------|----------|
| Retrieval Aug...    | Stage 4/7  | 2 hrs ago  | [Open]   |
| LLM Hallucinations  | Stage 2/7  | 1 day ago  | [Open]   |
| Meta-Learning...    | Complete   | 3 days ago | [View]   |
+----------------------------------------------------------+
| Showing 3 of 15 projects          [Load More] [Pagination]
+----------------------------------------------------------+
```

**Elements:**
- **Header:** Application title + "New Project" button (prominent, primary color)
- **Search Bar:** Filter projects by title/keywords (client-side or backend search)
- **Filter Dropdown:** "All", "In Progress", "Complete", "Draft"
- **Project Table/Cards:**
  - **Title:** Project name (clickable → opens project detail)
  - **Stage Progress:** "Stage X/7" or "Complete" (visual progress bar optional)
  - **Last Updated:** Relative time (e.g., "2 hours ago")
  - **Actions:** "Open" button (navigate to project detail page)
- **Pagination:** Load more / numbered pages if >20 projects

**Interactions:**
- Click project title or "Open" → Navigate to project detail view
- Click "New Project" → Show project creation modal/page
- Search input → Filter list in real-time
- Filter dropdown → Update visible projects

**Empty State:**
```
+----------------------------------------------------------+
|                                                          |
|               📚 No Projects Yet                         |
|                                                          |
|  Get started by creating your first research strategy.  |
|                                                          |
|                    [+ New Project]                       |
|                                                          |
+----------------------------------------------------------+
```

---

### 2. New Project Modal/Page

**Trigger:** Click "New Project" button

**Layout:**
```
+----------------------------------------------------------+
| Create New Project                             [X Close] |
+----------------------------------------------------------+
| What research question or topic would you like to        |
| explore?                                                 |
|                                                          |
| [____________________________________________]           |
| [____________________________________________]           |
| [____________________________________________]           |
| (Describe your research idea in 1-3 sentences)           |
|                                                          |
| Optional: Project Title (auto-generated if blank)        |
| [_________________________________]                      |
|                                                          |
|                        [Cancel]  [Create Project]        |
+----------------------------------------------------------+
```

**Fields:**
- **Research Idea (Textarea):** Required, placeholder: "e.g., Investigate techniques for reducing hallucinations in large language models using retrieval augmentation"
- **Project Title (Text Input):** Optional (backend auto-generates from idea if blank)

**Validation:**
- Research idea: minimum 20 characters, maximum 2000 characters
- Show character count below textarea

**Interactions:**
- Click "Create Project" → 
  - Validate inputs
  - Show loading spinner ("Creating project...")
  - POST to backend: `POST /api/projects` with `{raw_idea, title?}`
  - On success: Navigate to new project detail page (Stage 0 result)
  - On error: Show error message inline
- Click "Cancel" or [X] → Close modal without changes

---

## 🔌 API Integration

### Fetch Project List

**Endpoint:** `GET /api/projects`

**Response:**
```json
{
  "projects": [
    {
      "id": "project_abc123",
      "title": "Retrieval Augmentation for LLM Hallucination Mitigation",
      "current_stage": 4,
      "total_stages": 7,
      "status": "in_progress",
      "updated_at": "2025-11-22T10:30:00Z",
      "created_at": "2025-11-20T14:00:00Z"
    },
    ...
  ]
}
```

**Frontend Actions:**
- On mount: Fetch project list
- Display in table/cards
- Cache for 1 minute (optional)

---

### Create New Project

**Endpoint:** `POST /api/projects`

**Request Body:**
```json
{
  "raw_idea": "Investigate retrieval augmentation techniques for reducing LLM hallucinations",
  "title": "Retrieval Augmentation Study" // optional
}
```

**Response (Success):**
```json
{
  "project_id": "project_xyz789",
  "title": "Retrieval Augmentation Study",
  "stage_result": {
    "stage_name": "project-setup",
    "draft_artifact": {
      "id": "project_xyz789",
      "title": "Retrieval Augmentation Study",
      "short_description": "...",
      ...
    },
    "prompts": ["Review the generated project context...", ...],
    "validation_errors": []
  }
}
```

**Response (Error):**
```json
{
  "error": "Research idea must be at least 20 characters",
  "code": "VALIDATION_ERROR"
}
```

**Frontend Actions:**
- Disable "Create Project" button while loading
- Show spinner or progress indicator
- On success: Navigate to `/projects/{project_id}` (project detail page)
- On error: Display error message below form (red text or alert)

---

## 🎨 Design Specifications

### Colors (Tailwind CSS Classes as Reference)

- **Primary Action:** `bg-blue-600 hover:bg-blue-700 text-white`
- **Secondary Action:** `bg-gray-200 hover:bg-gray-300 text-gray-700`
- **Danger/Delete:** `bg-red-600 hover:bg-red-700 text-white`
- **Success Indicator:** `bg-green-600 text-white`
- **Stage Progress Bar:** `bg-blue-500` (filled), `bg-gray-200` (unfilled)

### Typography

- **Page Title:** 2xl font, semibold, gray-900
- **Project Title:** lg font, medium, gray-800, hover underline
- **Metadata (updated time):** sm font, gray-500
- **Button Text:** sm/base font, medium/semibold

### Spacing

- **Section Padding:** py-6 px-8
- **Table Row Padding:** py-3 px-4
- **Button Padding:** px-4 py-2 (small), px-6 py-3 (large)

### Responsive Behavior

- **Desktop (≥1024px):** Table view with all columns
- **Tablet (768-1023px):** Table view, hide "Updated" column, show on hover
- **Mobile (<768px):** Card view, stack project info vertically

```
Mobile Card Layout:
+--------------------------------+
| Retrieval Augmentation Study   |
| Stage 4/7 • 2 hours ago        |
| [■■■■■□□] 71% Complete          |
|                       [Open >] |
+--------------------------------+
```

---

## ♿ Accessibility Requirements

- **Keyboard Navigation:** Tab through projects, Enter to open
- **Screen Reader:** Announce project count, stage progress
- **ARIA Labels:** "Open project: {title}", "Create new project button"
- **Focus Indicators:** Visible focus ring on all interactive elements
- **Color Contrast:** WCAG AA minimum (4.5:1 for text)

---

## 🧪 Testing Scenarios

### Unit Tests
- [ ] Project list renders correctly with mock data
- [ ] Empty state shows when no projects
- [ ] Search filter works correctly
- [ ] New project modal validates input

### Integration Tests
- [ ] Create project API call succeeds and navigates to detail page
- [ ] Error handling displays backend validation errors
- [ ] Project list refreshes after creation

### E2E Tests
- [ ] User can create a new project end-to-end
- [ ] User can navigate from dashboard to project detail
- [ ] Search/filter updates visible projects

---

## 📝 Implementation Checklist

- [ ] Create `ProjectDashboard` component
- [ ] Create `ProjectListTable` component
- [ ] Create `ProjectCard` component (mobile)
- [ ] Create `NewProjectModal` component
- [ ] Implement `useProjects` hook (fetch project list)
- [ ] Implement `useCreateProject` mutation
- [ ] Add loading states (skeleton loaders)
- [ ] Add error states (retry buttons)
- [ ] Implement search/filter logic
- [ ] Add keyboard shortcuts (optional: `Cmd+N` for new project)
- [ ] Test on mobile/tablet/desktop
- [ ] Accessibility audit

---

## 🚀 Future Enhancements (Post-MVP)

- **Bulk Actions:** Delete/archive multiple projects
- **Project Templates:** Quick-start with pre-filled examples
- **Tags/Categories:** Organize projects by research area
- **Sharing:** Export project link for collaboration
- **Sorting:** Sort by title, date, stage progress
- **Advanced Filters:** By date range, stage, status

---

**Next:** Read `02_STAGE_EXECUTION.md` for the core pipeline interaction.


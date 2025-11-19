# Web UI for HITL Research Strategy Pipeline

A modern, user-friendly web interface for the Human-in-the-Loop Research Strategy Pipeline.

## Features

### 🎨 Modern UI/UX
- **Progressive disclosure**: Users see only what they need at each stage
- **Visual stage progression**: Timeline view with status indicators
- **Instant feedback**: HTMX-powered interactions without page reloads
- **Responsive design**: Works beautifully on desktop, tablet, and mobile
- **Accessible**: WCAG AA compliant with keyboard navigation

### ⚡ Technology Stack
- **Flask** - Lightweight Python web framework
- **HTMX** - Modern interactive UIs with minimal JavaScript
- **Tailwind CSS** - Utility-first CSS for rapid UI development
- **Alpine.js** - Lightweight JavaScript for dynamic components

### 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web server**:
   ```bash
   python interfaces/web_app.py
   ```

3. **Open your browser**:
   Navigate to `http://localhost:5000`

### 📱 User Journey

1. **Landing Page** → See your projects or start new
2. **New Project** → Enter research idea (AI extracts keywords)
3. **Project Detail** → Visual pipeline with stage progression
4. **Stage 0** → Review/edit project context → Approve
5. **Stage 1** → Review/edit problem framing → Approve
6. **Export** → Download strategy as Markdown/PDF

### 🎯 Key UX Patterns

#### Progressive Disclosure
Users aren't overwhelmed with all options at once. Each stage is its own focused page.

#### Visual Feedback
- **Green checkmark**: Stage approved
- **Yellow clock**: Draft/in review
- **Gray circle**: Not started
- **Spinners**: Loading states
- **Toast notifications**: Success/error messages

#### Contextual Help
- AI-generated review checklists at each stage
- Inline tips and examples
- Expandable help sections

#### Efficient Editing
- Inline tag management (keywords)
- Auto-expanding textareas
- Character counters
- One-click approval

### 📂 File Structure

```
templates/
├── base.html                 # Base layout with nav and styles
├── index.html                # Landing page with project list
├── new_project.html          # Project creation form
├── project_detail.html       # Stage progression overview
├── error.html                # Error page
└── stages/
    ├── project-setup.html    # Stage 0 edit/approve
    └── problem-framing.html  # Stage 1 edit/approve (to be created)

interfaces/
└── web_app.py               # Flask application

static/
├── css/                     # Custom CSS (optional)
└── js/                      # Custom JavaScript (optional)
```

### 🔌 API Endpoints

#### Pages
- `GET /` - Landing page
- `GET /project/new` - New project form
- `POST /project/new` - Create project
- `GET /project/<id>` - Project detail
- `GET /project/<id>/stage/<stage>` - Stage view

#### Actions
- `POST /project/<id>/stage/<stage>/run` - Execute stage
- `POST /project/<id>/stage/<stage>/approve` - Approve artifact

#### API (JSON)
- `GET /api/projects/<id>/artifacts/<type>` - Get artifact as JSON

### 🎨 Customization

#### Colors
Edit the status classes in `base.html`:
```css
.status-approved { @apply bg-green-100 text-green-800; }
.status-draft { @apply bg-yellow-100 text-yellow-800; }
.status-not_started { @apply bg-gray-100 text-gray-600; }
```

#### Branding
Update the logo and navigation in `base.html`:
```html
<a href="/" class="flex items-center">
    <!-- Your logo here -->
    <span class="ml-2 text-xl font-semibold">Your Branding</span>
</a>
```

### 🔧 Configuration

Set environment variables in `.env` (optional):
```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATA_DIR=./data
```

### 📊 Performance

- **HTMX**: Partial page updates reduce data transfer
- **Tailwind CDN**: For rapid prototyping (switch to build for production)
- **Alpine.js**: Only 3KB gzipped for interactivity
- **No jQuery**: Lightweight vanilla JavaScript

### 🧪 Testing

Run the Flask app in debug mode:
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python interfaces/web_app.py
```

### 📈 Next Steps

1. **Add remaining stages**:
   - Create templates for Stage 2-5
   - Follow the same pattern as project-setup.html

2. **Add export functionality**:
   - Markdown export route
   - PDF generation (using WeasyPrint)
   - Email delivery

3. **Add collaboration features**:
   - User authentication
   - Project sharing
   - Comments/annotations

4. **Add analytics**:
   - Track stage completion
   - Measure time per stage
   - User satisfaction surveys

### 🎓 UX Design Philosophy

See `docs/UX_DESIGN.md` for detailed UX principles and design decisions.

Key principles:
- **Clarity over cleverness** - Clear UI > flashy effects
- **Guidance over freedom** - Directed workflow for beginners
- **Flexibility for experts** - Keyboard shortcuts, bulk actions
- **Forgiveness** - Easy undo, auto-save drafts

### 🐛 Troubleshooting

**Issue**: Templates not found
- Ensure `templates/` directory exists
- Check Flask is running from project root

**Issue**: Static files not loading
- Create `static/` directory
- Check file paths in templates

**Issue**: HTMX not working
- Check browser console for errors
- Ensure CDN is accessible
- Test without HTMX (regular form submit)

### 📝 License

Same as the main project - see repository README.

---

**Live Demo**: Coming soon
**Documentation**: See `/docs` folder
**Issues**: GitHub Issues


# Design System for Strategy Pipeline

**Purpose:** Provide a consistent visual language and component specifications for the frontend team.

---

## 🎨 Color Palette

### Primary Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Primary Blue** | `#2563EB` | Primary actions, links, active states |
| **Primary Blue Hover** | `#1D4ED8` | Hover state for primary buttons |
| **Primary Blue Light** | `#DBEAFE` | Backgrounds, badges |

### Secondary Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Gray 50** | `#F9FAFB` | Page backgrounds |
| **Gray 100** | `#F3F4F6` | Card backgrounds, secondary backgrounds |
| **Gray 200** | `#E5E7EB` | Borders, dividers |
| **Gray 300** | `#D1D5DB` | Disabled states |
| **Gray 600** | `#4B5563` | Secondary text |
| **Gray 700** | `#374151` | Body text |
| **Gray 900** | `#111827` | Headings, primary text |

### Semantic Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Success Green** | `#10B981` | Success messages, approved status |
| **Success Light** | `#D1FAE5` | Success backgrounds |
| **Warning Yellow** | `#F59E0B` | Warning messages, draft status |
| **Warning Light** | `#FEF3C7` | Warning backgrounds |
| **Danger Red** | `#EF4444` | Error messages, destructive actions |
| **Danger Light** | `#FEE2E2` | Error backgrounds |
| **Info Blue** | `#3B82F6` | Informational messages |
| **Info Light** | `#DBEAFE` | Info backgrounds |

---

## 🖋 Typography

### Font Family

- **Primary:** `Inter, system-ui, -apple-system, sans-serif`
- **Monospace (Code):** `'Fira Code', 'Courier New', monospace`

### Font Sizes

| Name | Size | Line Height | Usage |
|------|------|-------------|-------|
| **xs** | 12px | 16px | Helper text, labels |
| **sm** | 14px | 20px | Body text, buttons |
| **base** | 16px | 24px | Default body text |
| **lg** | 18px | 28px | Large body text |
| **xl** | 20px | 28px | Subheadings |
| **2xl** | 24px | 32px | Section headings |
| **3xl** | 30px | 36px | Page titles |
| **4xl** | 36px | 40px | Hero headings |

### Font Weights

| Name | Weight | Usage |
|------|--------|-------|
| **Normal** | 400 | Body text |
| **Medium** | 500 | Emphasized text, buttons |
| **Semibold** | 600 | Subheadings |
| **Bold** | 700 | Headings, strong emphasis |

---

## 📏 Spacing Scale

Use a consistent spacing scale (8px base unit):

| Name | Size | Usage |
|------|------|-------|
| **0** | 0px | No spacing |
| **1** | 4px | Micro spacing |
| **2** | 8px | Small spacing |
| **3** | 12px | Default spacing |
| **4** | 16px | Medium spacing |
| **5** | 20px | Large spacing |
| **6** | 24px | Extra-large spacing |
| **8** | 32px | Section spacing |
| **10** | 40px | Page section spacing |
| **12** | 48px | Major section spacing |

---

## 🧩 Component Specifications

### Buttons

#### Primary Button
```css
background: #2563EB
color: #FFFFFF
padding: 10px 20px (sm), 12px 24px (base), 14px 28px (lg)
border-radius: 6px
font-weight: 500
font-size: 14px (sm), 16px (base)

Hover: background #1D4ED8
Active: background #1E40AF
Disabled: background #D1D5DB, color #9CA3AF
```

#### Secondary Button
```css
background: #F3F4F6
color: #374151
border: 1px solid #E5E7EB

Hover: background #E5E7EB
Active: background #D1D5DB
```

#### Danger Button
```css
background: #EF4444
color: #FFFFFF

Hover: background #DC2626
```

#### Ghost Button
```css
background: transparent
color: #374151

Hover: background #F3F4F6
```

---

### Input Fields

#### Text Input
```css
border: 1px solid #D1D5DB
border-radius: 6px
padding: 8px 12px (sm), 10px 14px (base)
font-size: 14px (sm), 16px (base)
background: #FFFFFF

Focus: border-color #2563EB, box-shadow 0 0 0 3px rgba(37, 99, 235, 0.1)
Error: border-color #EF4444
Disabled: background #F9FAFB, color #9CA3AF
```

#### Textarea
```css
Same as text input
min-height: 100px
resize: vertical
```

#### Select Dropdown
```css
Same as text input
appearance: none
padding-right: 36px (for dropdown icon)
```

---

### Cards

```css
background: #FFFFFF
border: 1px solid #E5E7EB
border-radius: 8px
padding: 16px (sm), 24px (base), 32px (lg)
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)

Hover (if interactive): box-shadow 0 4px 6px rgba(0, 0, 0, 0.1)
```

---

### Badges

#### Status Badge
```css
padding: 4px 12px
border-radius: 12px (fully rounded)
font-size: 12px
font-weight: 500
display: inline-flex
align-items: center

Variants:
- Draft: background #FEF3C7, color #92400E
- Approved: background #D1FAE5, color #065F46
- Error: background #FEE2E2, color #991B1B
- Locked: background #F3F4F6, color #4B5563
```

---

### Modals

```css
Overlay: background rgba(0, 0, 0, 0.5)

Content:
  background: #FFFFFF
  border-radius: 12px
  padding: 24px
  max-width: 600px
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15)

Header:
  font-size: 20px
  font-weight: 600
  margin-bottom: 16px

Footer:
  margin-top: 24px
  display: flex
  justify-content: flex-end
  gap: 12px
```

---

### Progress Bars

```css
height: 8px
background: #E5E7EB
border-radius: 4px

Fill:
  background: #2563EB
  border-radius: 4px
  transition: width 0.3s ease

Variants:
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
```

---

### Stage Stepper

```css
Circle (Completed):
  width: 32px
  height: 32px
  background: #2563EB
  color: #FFFFFF
  border-radius: 50%
  display: flex
  align-items: center
  justify-content: center
  font-weight: 600

Circle (Current):
  border: 3px solid #2563EB
  background: #FFFFFF
  color: #2563EB
  animation: pulse 2s infinite

Circle (Locked):
  background: #E5E7EB
  color: #9CA3AF

Connector:
  height: 2px
  background: #E5E7EB (future)
  background: #2563EB (completed)
```

---

## 🎭 Icons

**Recommended Icon Library:** Heroicons, Lucide, or Font Awesome

**Icon Sizes:**
- **sm:** 16x16px
- **base:** 20x20px
- **lg:** 24x24px
- **xl:** 32x32px

**Common Icons:**
- **Check (✓):** Approved status
- **Clock (⏱):** Draft, in-progress
- **Lock (🔒):** Locked stage
- **Alert (⚠️):** Warning, error
- **Plus (+):** Add item
- **X:** Remove item, close modal
- **Pencil (✏️):** Edit action
- **Play (▶):** Run stage
- **Download (⬇):** Export

---

## 🌈 Shadows

```css
sm: 0 1px 2px rgba(0, 0, 0, 0.05)
base: 0 1px 3px rgba(0, 0, 0, 0.1)
md: 0 4px 6px rgba(0, 0, 0, 0.1)
lg: 0 10px 15px rgba(0, 0, 0, 0.1)
xl: 0 20px 25px rgba(0, 0, 0, 0.15)
```

---

## 📱 Responsive Breakpoints

```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra-large desktop */
```

---

## ♿ Accessibility

### Focus States
- **Visible focus ring:** 3px solid ring with 2px offset, color: `#2563EB`
- **Skip to content link:** For keyboard navigation

### Color Contrast
- **Text on background:** Minimum 4.5:1 (WCAG AA)
- **Large text (≥18px):** Minimum 3:1
- **Interactive elements:** Minimum 3:1 against background

### ARIA Labels
- All interactive elements must have accessible names
- Form inputs must have associated labels
- Status changes must be announced to screen readers

---

## 🎬 Animations

### Transitions

```css
Default: transition-all 150ms ease-in-out
Slow: transition-all 300ms ease-in-out
Fast: transition-all 100ms ease-in-out
```

### Common Animations

**Fade In:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
animation: fadeIn 200ms ease-in;
```

**Slide In:**
```css
@keyframes slideIn {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
animation: slideIn 200ms ease-out;
```

**Pulse (for current stage):**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
animation: pulse 2s infinite;
```

---

## 🧪 Example Component: Button

```jsx
// React example with Tailwind CSS
<button className="
  px-6 py-3 
  bg-blue-600 hover:bg-blue-700 
  text-white font-medium 
  rounded-lg 
  transition-colors duration-150 
  focus:outline-none focus:ring-3 focus:ring-blue-500 focus:ring-offset-2
  disabled:bg-gray-300 disabled:cursor-not-allowed
">
  Run Stage 1
</button>
```

---

**Note:** This design system is stack-agnostic. Adapt class names to your chosen CSS framework (Tailwind, CSS Modules, styled-components, etc.).


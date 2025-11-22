# Strategy Pipeline UI

Modern, type-safe frontend for the Strategy Pipeline SLR automation platform.

## 🚀 Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Router** - Type-safe routing with file-based routes
- **TanStack Query** - Server state management
- **TanStack Table** - Headless table logic
- **Tailwind CSS 4** - Utility-first styling
- **shadcn/ui** - High-quality UI components
- **Lucide React** - Icon library

## 📋 Prerequisites

- Node.js 18+ 
- npm or pnpm
- Strategy Pipeline backend running on `http://localhost:5000`

## 🛠️ Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file:

```env
VITE_API_BASE_URL=http://localhost:5000
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── ProjectDashboard.tsx
│   ├── ProjectDetail.tsx
│   ├── StageView.tsx
│   └── NewProjectDialog.tsx
├── lib/
│   ├── api/            # API client and React Query hooks
│   │   ├── client.ts   # Fetch wrapper
│   │   ├── projects.ts # Project API endpoints
│   │   └── hooks.ts    # React Query hooks
│   └── utils.ts        # Utility functions
├── routes/             # File-based routing
│   ├── __root.tsx      # Root layout
│   ├── index.tsx       # Project dashboard
│   └── projects/
│       ├── $projectId.tsx           # Project detail
│       └── $projectId/
│           └── stages/
│               └── $stageName.tsx   # Stage view
├── types/              # TypeScript type definitions
│   └── project.ts      # Project, stage, and artifact types
└── main.tsx           # App entry point
```

## 🎯 Key Features

### Type-Safe Routing

Routes are automatically typed based on file structure:

```typescript
// Navigate with full type safety
navigate({ 
  to: '/projects/$projectId', 
  params: { projectId: '123' } 
})
```

### Server State Management

React Query hooks for all API calls:

```typescript
// Automatic caching, refetching, and error handling
const { data: projects, isLoading } = useProjects()
const createProject = useCreateProject()
```

### Responsive UI

Built with Tailwind CSS and shadcn/ui components for a consistent, accessible design.

## 🔌 API Integration

The frontend communicates with the Flask backend via REST API:

- `GET /api/projects/{id}/artifacts/{type}` - Fetch artifacts
- `POST /project/new` - Create project
- `POST /project/{id}/stage/{name}/run` - Run stage
- `POST /project/{id}/stage/{name}/approve` - Approve stage

See `src/lib/api/` for full API client implementation.

## 🎨 Adding UI Components

This project uses shadcn/ui. To add new components:

```bash
npx shadcn@latest add <component-name>
```

Example:
```bash
npx shadcn@latest add dialog table badge
```

## 📝 Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run check` - Format and lint
- `npm test` - Run tests with Vitest

## 🏗️ Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

To preview the build:

```bash
npm run preview
```

## 🔧 Configuration

### Vite Config

See `vite.config.ts` for build configuration, including:
- React plugin with compiler
- TanStack Router file-based routing
- Tailwind CSS
- Path aliases (`@/` → `src/`)

### TypeScript Config

See `tsconfig.json` for TypeScript configuration with strict mode enabled.

### Tailwind Config

Theme variables are defined in `src/styles.css` using CSS custom properties for easy theming.

## 🚦 Development Workflow

### 1. Create a New Route

Add a file to `src/routes/`:

```typescript
// src/routes/about.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/about')({
  component: AboutPage,
})

function AboutPage() {
  return <div>About</div>
}
```

The route tree is automatically regenerated.

### 2. Add API Endpoints

Add to `src/lib/api/projects.ts`:

```typescript
export const projectsApi = {
  // ... existing methods
  
  delete: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/api/projects/${projectId}`)
  },
}
```

### 3. Create React Query Hook

Add to `src/lib/api/hooks.ts`:

```typescript
export function useDeleteProject() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (projectId: string) => projectsApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects })
    },
  })
}
```

### 4. Use in Component

```typescript
const deleteProject = useDeleteProject()

const handleDelete = async (id: string) => {
  await deleteProject.mutateAsync(id)
}
```

## 🐛 Troubleshooting

### Backend Connection Issues

Ensure the backend is running and `VITE_API_BASE_URL` is correctly set.

### Route Type Errors

If routes aren't typed correctly, regenerate the route tree:

```bash
npx tsr generate
```

### Build Errors

Clear the build cache:

```bash
rm -rf node_modules/.vite dist
npm install
npm run build
```

## 📚 Learn More

- [TanStack Router Docs](https://tanstack.com/router)
- [TanStack Query Docs](https://tanstack.com/query)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Tailwind CSS Docs](https://tailwindcss.com)
- [Vite Docs](https://vitejs.dev)

## 📄 License

Same as parent project.


# Development Guide

## Architecture Overview

### Component Hierarchy

```
App
├── __root (Header + Outlet)
├── / (ProjectDashboard)
│   └── NewProjectDialog
├── /projects/$projectId (ProjectDetail)
│   └── Stage Timeline
└── /projects/$projectId/stages/$stageName (StageView)
    └── Artifact Forms
```

### Data Flow

1. **React Query** manages all server state
2. **TanStack Router** provides type-safe navigation
3. **API Client** handles all HTTP requests
4. **Components** are purely presentational

### State Management Strategy

- **Server State**: TanStack Query (projects, artifacts)
- **UI State**: React useState (modals, forms)
- **URL State**: TanStack Router (current project/stage)
- **No Global State**: Keep components isolated

## API Integration Patterns

### Fetching Data

```typescript
// In component
const { data, isLoading, error } = useArtifact<ProjectContext>(
  projectId,
  'ProjectContext'
)

// The hook definition
export function useArtifact<T>(projectId: string, artifactType: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'artifacts', artifactType],
    queryFn: () => projectsApi.getArtifact<T>(projectId, artifactType),
    enabled: !!projectId && !!artifactType,
  })
}
```

### Mutations

```typescript
// In component
const createProject = useCreateProject()

const handleSubmit = async () => {
  try {
    const result = await createProject.mutateAsync(rawIdea)
    navigate({ to: '/projects/$projectId', params: { projectId: result.project_id } })
  } catch (error) {
    // Handle error
  }
}

// The hook definition
export function useCreateProject() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (rawIdea: string) => projectsApi.create(rawIdea),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}
```

### Cache Invalidation

```typescript
// Invalidate specific query
queryClient.invalidateQueries({ 
  queryKey: ['projects', projectId] 
})

// Invalidate all project queries
queryClient.invalidateQueries({ 
  queryKey: ['projects'] 
})

// Update cache optimistically
queryClient.setQueryData(['projects', projectId], (old) => ({
  ...old,
  status: 'approved',
}))
```

## Routing Patterns

### File-Based Routes

Routes are defined by file structure:

```
routes/
  __root.tsx              → /
  index.tsx               → /
  projects/
    $projectId.tsx        → /projects/:projectId
    $projectId/
      stages/
        $stageName.tsx    → /projects/:projectId/stages/:stageName
```

### Navigation

```typescript
// Type-safe navigation
import { Link, useNavigate } from '@tanstack/react-router'

// Links
<Link 
  to="/projects/$projectId" 
  params={{ projectId: '123' }}
>
  View Project
</Link>

// Programmatic
const navigate = useNavigate()
navigate({ 
  to: '/projects/$projectId/stages/$stageName',
  params: { projectId: '123', stageName: 'problem-framing' }
})
```

### Route Parameters

```typescript
// In component
import { useParams } from '@tanstack/react-router'

const { projectId, stageName } = useParams({ strict: false }) as {
  projectId: string
  stageName: string
}
```

## Component Patterns

### Page Components

Located in `src/components/`, these are full-page views:

- `ProjectDashboard.tsx` - List all projects
- `ProjectDetail.tsx` - Show project with stage timeline
- `StageView.tsx` - Display and edit stage artifacts

### UI Components

Located in `src/components/ui/`, these are reusable shadcn/ui components:

- `button.tsx`, `input.tsx`, `card.tsx`, etc.
- Follow shadcn/ui patterns
- Fully typed with TypeScript

### Component Structure

```typescript
/**
 * Component documentation
 */
import { ... } from '...'

interface ComponentProps {
  // Props with JSDoc comments
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  // Hooks first
  const navigate = useNavigate()
  const { data, isLoading } = useQuery(...)
  const mutation = useMutation(...)
  
  // Event handlers
  const handleAction = async () => {
    // ...
  }
  
  // Early returns for loading/error states
  if (isLoading) return <Loading />
  if (error) return <Error />
  
  // Main render
  return (
    <div>
      {/* Component JSX */}
    </div>
  )
}
```

## Styling Patterns

### Tailwind CSS

Use utility classes for all styling:

```typescript
<div className="flex items-center justify-between gap-4 p-6">
  <h1 className="text-2xl font-bold text-foreground">Title</h1>
  <Button variant="outline" size="sm">Action</Button>
</div>
```

### Theme Variables

Defined in `src/styles.css`:

```css
:root {
  --background: oklch(...);
  --foreground: oklch(...);
  --primary: oklch(...);
  /* etc */
}
```

Use in components via Tailwind:

```typescript
<div className="bg-background text-foreground border-border">
  Content
</div>
```

### Component Variants

Use `class-variance-authority` for variant-based styling:

```typescript
import { cva } from 'class-variance-authority'

const buttonVariants = cva(
  'base-classes',
  {
    variants: {
      variant: {
        default: 'default-classes',
        outline: 'outline-classes',
      },
      size: {
        sm: 'sm-classes',
        lg: 'lg-classes',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'sm',
    },
  }
)
```

## Type Safety

### Type Definitions

All types are in `src/types/project.ts`:

```typescript
export interface Project {
  id: string
  title: string
  status: ProjectStatus
  // ...
}

export type ProjectStatus = 'draft' | 'in_progress' | 'completed'
```

### Generic API Calls

```typescript
// Type the response
const { data } = useArtifact<ProjectContext>(projectId, 'ProjectContext')

// TypeScript knows data is ProjectContext
console.log(data.title) // ✅
console.log(data.invalid) // ❌ Type error
```

### Route Types

Routes are automatically typed:

```typescript
// ✅ Valid
<Link to="/projects/$projectId" params={{ projectId: '123' }} />

// ❌ Type error - missing params
<Link to="/projects/$projectId" />

// ❌ Type error - invalid route
<Link to="/invalid-route" />
```

## Error Handling

### API Errors

```typescript
const { data, error, isError } = useQuery(...)

if (isError) {
  return (
    <Card className="border-destructive">
      <CardContent className="pt-6">
        <p className="text-destructive">
          {error.message || 'Failed to load data'}
        </p>
      </CardContent>
    </Card>
  )
}
```

### Mutation Errors

```typescript
const mutation = useMutation(...)

const handleSubmit = async () => {
  try {
    await mutation.mutateAsync(data)
    // Success
  } catch (error) {
    console.error('Mutation failed:', error)
    // Show error to user
  }
}

// Or show inline
{mutation.isError && (
  <p className="text-sm text-destructive">
    {mutation.error.message}
  </p>
)}
```

## Testing Strategy

### Component Tests

```typescript
import { render, screen } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'
import ProjectDashboard from './ProjectDashboard'

test('renders project list', () => {
  render(
    <QueryClientProvider client={queryClient}>
      <ProjectDashboard />
    </QueryClientProvider>
  )
  
  expect(screen.getByText('Strategy Pipeline')).toBeInTheDocument()
})
```

### API Mocking

Use MSW (Mock Service Worker) for API mocking:

```typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/projects/:id/artifacts/:type', (req, res, ctx) => {
    return res(ctx.json({ /* mock data */ }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## Performance Optimization

### Code Splitting

Routes are automatically code-split:

```typescript
// vite.config.ts
tanstackRouter({
  target: 'react',
  autoCodeSplitting: true, // ✅ Enabled
})
```

### Query Stale Time

Configure how long data stays fresh:

```typescript
// src/lib/queryClient.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})
```

### React Compiler

Automatic memoization via Babel plugin:

```typescript
// vite.config.ts
viteReact({
  babel: {
    plugins: ['babel-plugin-react-compiler'], // ✅ Enabled
  },
})
```

## Common Tasks

### Adding a New Page

1. Create route file: `src/routes/new-page.tsx`
2. Define route:
   ```typescript
   export const Route = createFileRoute('/new-page')({
     component: NewPage,
   })
   ```
3. Route tree auto-updates

### Adding a New API Endpoint

1. Add to `src/lib/api/projects.ts`
2. Create hook in `src/lib/api/hooks.ts`
3. Use in component

### Adding a New shadcn Component

```bash
npx shadcn@latest add dialog
```

Component will be added to `src/components/ui/`

### Updating Types

1. Edit `src/types/project.ts`
2. TypeScript will show errors where updates needed
3. Fix type errors across codebase

## Debugging

### React Query Devtools

Automatically available in dev mode at bottom-right of screen.

### TanStack Router Devtools

Available in dev mode. Shows route tree and active routes.

### Console Logging

API client logs all errors:

```typescript
// In src/lib/api/client.ts
catch (error) {
  console.error(`API Error [${endpoint}]:`, error)
  throw error
}
```

## Best Practices

1. **Keep components small** - Split large components into smaller ones
2. **Use TypeScript strictly** - Enable all strict flags
3. **Handle loading states** - Always show loading UI
4. **Handle errors gracefully** - Show user-friendly error messages
5. **Use semantic HTML** - Accessibility first
6. **Follow shadcn/ui patterns** - Consistency across UI
7. **Test edge cases** - Empty states, errors, slow network
8. **Document complex logic** - Add JSDoc comments
9. **Keep API client thin** - Logic in React Query hooks
10. **Invalidate queries correctly** - Keep cache fresh

## Troubleshooting

### "Module not found" errors

```bash
# Clear cache and reinstall
rm -rf node_modules .vite
npm install
```

### Route types not updating

```bash
# Regenerate route tree
npx tsr generate
```

### Styles not applying

```bash
# Check Tailwind config
# Ensure proper @import in styles.css
# Restart dev server
```

### API calls failing

1. Check backend is running
2. Verify `VITE_API_BASE_URL` in `.env.local`
3. Check browser network tab
4. Check backend logs


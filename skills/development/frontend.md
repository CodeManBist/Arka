# Frontend Development Skills

## 🎯 Overview

Skills for developing the Blast Radius frontend using Next.js, React, TypeScript, and Tailwind CSS.

## 📋 Prerequisites

- Node.js 22+
- npm or yarn
- TypeScript knowledge
- React hooks and components
- Tailwind CSS for styling

## 🏗️ Core Concepts

### Project Structure

```
frontend/
├── app/
│   ├── blast-radius/
│   │   └── page.tsx          # Main application page
│   ├── page.tsx              # Landing page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── public/                   # Static assets
├── package.json
├── tsconfig.json
└── next.config.ts
```

### Next.js App Router

- Uses the App Router (Next.js 13+)
- Server Components by default
- Client Components with 'use client' directive
- File-based routing

## 🛠️ Required Tools

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start
```

## 📚 Common Patterns

### 1. Client Components

```tsx
'use client';

import { useState, useEffect } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### 2. API Calls

```tsx
'use client';

import { useState } from 'react';

interface RepositoryOverview {
  repository: string;
  total_files: number;
  language_breakdown: Record<string, number>;
}

export default function RepositoryStats() {
  const [overview, setOverview] = useState<RepositoryOverview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async (repoPath: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/blast-radius/repository-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repository_path: repoPath }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setOverview(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {overview && (
        <div>
          <h2>{overview.repository}</h2>
          <p>Total files: {overview.total_files}</p>
        </div>
      )}
    </div>
  );
}
```

### 3. Form Handling

```tsx
'use client';

import { useState } from 'react';

export default function RepositoryForm() {
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Call API
      await fetchRepositoryOverview(repoUrl);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">
          Repository URL
        </label>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button
        type="submit"
        disabled={isLoading || !repoUrl}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
      >
        {isLoading ? 'Loading...' : 'Analyze Repository'}
      </button>
    </form>
  );
}
```

### 4. Dark Mode Support

```tsx
// In layout.tsx or globals.css

// Use CSS variables for dark mode
:root {
  --background: #ffffff;
  --foreground: #171717;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
}

// In components
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  {/* Content */}
</div>
```

### 5. Tab Navigation

```tsx
'use client';

import { useState } from 'react';

type Tab = 'overview' | 'analyze' | 'diff' | 'visualize';

export default function Tabs() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const tabs = [
    { id: 'overview', label: '📊 Repository Overview' },
    { id: 'analyze', label: '🎯 Analyze Symbol' },
    { id: 'diff', label: '🔥 Diff Analysis' },
    { id: 'visualize', label: '🌐 Visualize Graph' },
  ];

  return (
    <div className="mb-8">
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as Tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      <div className="mt-4">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'analyze' && <AnalyzeTab />}
        {activeTab === 'diff' && <DiffTab />}
        {activeTab === 'visualize' && <VisualizeTab />}
      </div>
    </div>
  );
}
```

### 6. Risk Badges

```tsx
interface RiskBadgeProps {
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

export default function RiskBadge({ riskLevel }: RiskBadgeProps) {
  const colors = {
    low: 'bg-green-600 text-white',
    medium: 'bg-yellow-500 text-black',
    high: 'bg-orange-600 text-white',
    critical: 'bg-red-600 text-white',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[riskLevel]}`}>
      {riskLevel.toUpperCase()}
    </span>
  );
}
```

### 7. Copy to Clipboard

```tsx
'use client';

export default function CopyButton({ text }: { text: string }) {
  const copyToClipboard = () => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    }).catch(() => {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert('Copied to clipboard!');
    });
  };

  return (
    <button
      onClick={copyToClipboard}
      className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 px-3 py-1 rounded-lg text-sm font-medium transition-colors"
    >
      Copy
    </button>
  );
}
```

## 🎯 Best Practices

### 1. Component Organization

- Keep components small and focused
- Use descriptive names
- Separate concerns (UI vs logic)
- Use TypeScript interfaces for props

### 2. Styling

- Use Tailwind CSS utility classes
- Follow consistent spacing (4px, 8px, 12px, etc.)
- Use dark mode variants (`dark:` prefix)
- Avoid inline styles

### 3. Performance

- Use `useMemo` for expensive calculations
- Use `useCallback` for event handlers
- Implement virtualization for large lists
- Lazy load non-critical components

### 4. Error Handling

```tsx
const [error, setError] = useState<string | null>(null);

// In API calls
try {
  // ... API call
} catch (err) {
  setError(err instanceof Error ? err.message : 'An error occurred');
} finally {
  setLoading(false);
}

// Display error
{error && (
  <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
    <p>⚠️ {error}</p>
    <button onClick={() => setError(null)} className="mt-2 text-sm underline hover:no-underline">
      Dismiss
    </button>
  </div>
)}
```

### 5. Loading States

```tsx
if (isLoading) {
  return (
    <div className="flex items-center justify-center py-8">
      <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>
  );
}
```

## 🧪 Testing

### Test Component Rendering

```tsx
// __tests__/components/RiskBadge.test.tsx
import { render, screen } from '@testing-library/react';
import RiskBadge from '@/components/RiskBadge';

describe('RiskBadge', () => {
  it('renders correctly for each risk level', () => {
    const riskLevels = ['low', 'medium', 'high', 'critical'] as const;
    
    riskLevels.forEach((level) => {
      render(<RiskBadge riskLevel={level} />);
      expect(screen.getByText(level.toUpperCase())).toBeInTheDocument();
    });
  });
});
```

### Test API Integration

```tsx
// __tests__/api/blastRadius.test.tsx
import { fetchRepositoryOverview } from '@/lib/api';

global.fetch = jest.fn();

describe('fetchRepositoryOverview', () => {
  it('fetches repository overview successfully', async () => {
    const mockData = {
      repository: 'test-repo',
      total_files: 10,
      language_breakdown: { python: 5, javascript: 5 }
    };
    
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData)
    });
    
    const result = await fetchRepositoryOverview('/path/to/repo');
    expect(result).toEqual(mockData);
  });
});
```

## 📖 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🚨 Troubleshooting

### TypeScript Errors
- Check type definitions
- Use proper interfaces for props
- Add type assertions when needed

### Styling Issues
- Verify Tailwind CSS is properly configured
- Check for missing classes
- Use the correct dark mode variants

### API Connection Issues
- Verify CORS headers on the backend
- Check network connectivity
- Test API endpoints with curl or Postman

### Build Errors
- Delete `.next` directory and rebuild
- Check Node.js version compatibility
- Verify all dependencies are installed
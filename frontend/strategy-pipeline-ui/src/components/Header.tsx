import { Link } from '@tanstack/react-router'
import { Home, Menu, X, BookOpen } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80">
            <BookOpen className="h-6 w-6" />
            <span className="text-xl font-bold">Strategy Pipeline</span>
          </Link>

          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 hover:bg-accent rounded-lg"
            aria-label="Toggle menu"
          >
            <Menu size={24} />
          </button>

          <nav className="hidden md:flex items-center gap-4">
            <Link
              to="/"
              className="px-4 py-2 rounded-lg hover:bg-accent transition-colors"
              activeProps={{ className: 'bg-accent' }}
            >
              Projects
            </Link>
          </nav>
        </div>
      </header>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setIsOpen(false)}
          />
          <aside className="absolute top-0 left-0 h-full w-64 bg-background shadow-lg">
            <div className="flex items-center justify-between p-4 border-b">
              <span className="font-bold">Menu</span>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-accent rounded-lg"
              >
                <X size={20} />
              </button>
            </div>
            <nav className="p-4">
              <Link
                to="/"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors"
                activeProps={{ className: 'bg-accent' }}
              >
                <Home size={20} />
                Projects
              </Link>
            </nav>
          </aside>
        </div>
      )}
    </>
  )
}

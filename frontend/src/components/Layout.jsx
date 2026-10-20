import { FiHome } from 'react-icons/fi'
import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-[#1a1a2e] to-[#16213e] text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition">
            <FiHome className="text-2xl" />
            <div>
              <h1 className="text-xl font-bold tracking-tight">E2M Solutions</h1>
              <p className="text-xs text-blue-200">AI-Powered Exterior Renovation Planner</p>
            </div>
          </Link>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-200 text-center text-sm text-gray-500 py-3">
        E2M Solutions © 2025 — Advisory estimates only
      </footer>
    </div>
  )
}

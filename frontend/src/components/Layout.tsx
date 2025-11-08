import { Outlet, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Home, 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  AlertTriangle,
  Menu,
  X,
  UserPlus
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Create Verification', href: '/verifications/create', icon: UserPlus },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Verifications', href: '/verifications', icon: CheckCircle },
  { name: 'Fraud Detection', href: '/fraud', icon: AlertTriangle },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <div
        className={cn(
          'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm lg:hidden',
          sidebarOpen ? 'block' : 'hidden'
        )}
        onClick={() => setSidebarOpen(false)}
      >
        <div
          className="fixed inset-y-0 left-0 w-64 bg-card border-r border-border"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h1 className="text-xl font-bold text-foreground">Hirefy</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-md hover:bg-accent"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <nav className="p-4 space-y-2">
            {navigation.map((item, index) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    to={item.href}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all',
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-sm'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground hover:translate-x-1'
                    )}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="h-5 w-5" />
                    {item.name}
                  </Link>
                </motion.div>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 border-r border-border bg-card">
          <motion.div 
            className="flex items-center h-16 px-6 border-b border-border"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className="text-xl font-bold text-foreground bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Hirefy
            </h1>
          </motion.div>
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item, index) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    to={item.href}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all',
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-sm'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground hover:translate-x-1'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.name}
                  </Link>
                </motion.div>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="sticky top-0 z-40 flex items-center h-16 px-4 border-b border-border bg-card/95 backdrop-blur-sm lg:hidden">
          <motion.button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md hover:bg-accent transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Menu className="h-6 w-6" />
          </motion.button>
          <h1 className="ml-4 text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Hirefy
          </h1>
        </div>

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

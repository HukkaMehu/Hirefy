"use client";

import { ReactNode, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  FileSearch, 
  Upload, 
  Settings, 
  Shield,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/src/components/ui/button';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarProvider,
  SidebarTrigger,
} from '@/src/components/ui/sidebar';
import { fadeIn, slideLeft } from '@/lib/animations';

interface DashboardLayoutProps {
  children: ReactNode;
}

const navigation = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, href: '/dashboard' },
  { id: 'verifications', label: 'Verifications', icon: FileSearch, href: '/dashboard/verifications' },
  { id: 'new', label: 'New Verification', icon: Upload, href: '/dashboard/new' },
];

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname?.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1a] to-[#0a0a0f]">
      <SidebarProvider>
        {/* Desktop Sidebar */}
        <motion.aside 
          initial="initial"
          animate="animate"
          variants={slideLeft}
          className="hidden lg:block fixed left-0 top-0 h-full w-64 glass border-r border-white/10 z-50"
        >
          <div className="flex flex-col h-full p-6">
            {/* Logo */}
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold gradient-text">TruthHire</h3>
                <p className="text-xs text-[#6b7280]">AI Verification</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                    onClick={() => router.push(item.href)}
                    className={`w-full justify-start gap-3 h-12 ${
                      active
                        ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 text-white border border-purple-500/50 hover:bg-gradient-to-r hover:from-purple-600/30 hover:to-blue-600/30'
                        : 'text-[#9ca3af] hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm">{item.label}</span>
                  </Button>
                );
              })}
            </nav>

            {/* Footer Actions */}
            <div className="space-y-2 pt-6 border-t border-white/10">
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 h-12 text-[#9ca3af] hover:bg-white/5 hover:text-white"
                onClick={() => router.push('/settings')}
              >
                <Settings className="w-5 h-5" />
                <span className="text-sm">Settings</span>
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 h-12 text-[#9ca3af] hover:bg-white/5 hover:text-red-400"
                onClick={() => {
                  // Add logout logic here
                  console.log('Logout clicked');
                }}
              >
                <LogOut className="w-5 h-5" />
                <span className="text-sm">Logout</span>
              </Button>
            </div>
          </div>
        </motion.aside>

        {/* Mobile Menu Button */}
        <div className="lg:hidden fixed top-4 left-4 z-50">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="glass border border-white/10"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Drawer */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setMobileMenuOpen(false)}
                className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
              />
              
              {/* Drawer */}
              <motion.aside
                initial={{ x: -300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="lg:hidden fixed left-0 top-0 h-full w-64 glass border-r border-white/10 z-50"
              >
                <div className="flex flex-col h-full p-6">
                  {/* Logo */}
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                      <Shield className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold gradient-text">TruthHire</h3>
                      <p className="text-xs text-[#6b7280]">AI Verification</p>
                    </div>
                  </div>

                  {/* Navigation */}
                  <nav className="flex-1 space-y-2">
                    {navigation.map((item) => {
                      const Icon = item.icon;
                      const active = isActive(item.href);
                      
                      return (
                        <Button
                          key={item.id}
                          variant="ghost"
                          onClick={() => {
                            router.push(item.href);
                            setMobileMenuOpen(false);
                          }}
                          className={`w-full justify-start gap-3 h-12 ${
                            active
                              ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 text-white border border-purple-500/50'
                              : 'text-[#9ca3af] hover:bg-white/5 hover:text-white'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          <span className="text-sm">{item.label}</span>
                        </Button>
                      );
                    })}
                  </nav>

                  {/* Footer Actions */}
                  <div className="space-y-2 pt-6 border-t border-white/10">
                    <Button
                      variant="ghost"
                      className="w-full justify-start gap-3 h-12 text-[#9ca3af] hover:bg-white/5 hover:text-white"
                      onClick={() => {
                        router.push('/settings');
                        setMobileMenuOpen(false);
                      }}
                    >
                      <Settings className="w-5 h-5" />
                      <span className="text-sm">Settings</span>
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start gap-3 h-12 text-[#9ca3af] hover:bg-white/5 hover:text-red-400"
                      onClick={() => {
                        // Add logout logic here
                        setMobileMenuOpen(false);
                        console.log('Logout clicked');
                      }}
                    >
                      <LogOut className="w-5 h-5" />
                      <span className="text-sm">Logout</span>
                    </Button>
                  </div>
                </div>
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <motion.main 
          initial="initial"
          animate="animate"
          variants={fadeIn}
          className="lg:ml-64 min-h-screen"
        >
          <div className="p-6 lg:p-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {children}
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.main>
      </SidebarProvider>
    </div>
  );
}

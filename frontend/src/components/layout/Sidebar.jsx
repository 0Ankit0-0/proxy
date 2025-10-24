import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  FileText,
  Shield,
  RefreshCw,
  FileBarChart,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap
} from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

const Sidebar = ({ activeView, onViewChange, isCollapsed, onToggleCollapse }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'logs', label: 'Log Collection', icon: FileText },
    { id: 'threats', label: 'Threat Analysis', icon: Shield },
    { id: 'soup', label: 'SOUP Updates', icon: RefreshCw },
    { id: 'reports', label: 'Reports', icon: FileBarChart },
    { id: 'system', label: 'System Status', icon: Settings }
  ];

  return (
    <motion.aside
      className={cn(
        "bg-secondary border-r border-border h-screen flex flex-col fixed left-0 top-0 z-10",
        isCollapsed ? "w-20" : "w-70"
      )}
      animate={{ width: isCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <div className="p-6 border-b border-border flex items-center gap-4 relative">
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-4 flex-1"
            >
              <motion.div
                className="text-3xl leading-none text-accent"
                whileHover={{ scale: 1.1, rotate: 10 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <Zap />
              </motion.div>
              <div className="flex-1">
                <h1 className="text-lg font-bold text-accent">Project Quorum</h1>
                <p className="text-xs text-muted-foreground">Offline Log Intelligence</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 hover:bg-accent/10 hover:text-accent"
          onClick={onToggleCollapse}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </motion.div>
        </Button>
      </div>

      <nav className="flex-1 p-4 flex flex-col gap-1">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05, duration: 0.2 }}
            >
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start gap-4 h-12 px-4 text-muted-foreground hover:bg-accent/10 hover:text-foreground",
                  isActive && "bg-accent/20 text-accent border-l-4 border-accent"
                )}
                onClick={() => onViewChange(item.id)}
              >
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-4"
                >
                  <Icon className="h-5 w-5 min-w-5" />
                  <AnimatePresence>
                    {!isCollapsed && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "auto" }}
                        exit={{ opacity: 0, width: 0 }}
                        transition={{ duration: 0.2 }}
                        className="truncate"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.div>
              </Button>
            </motion.div>
          );
        })}
      </nav>
    </motion.aside>
  );
};

export default Sidebar;

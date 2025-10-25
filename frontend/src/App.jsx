import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import LogCollection from './pages/LogCollection';
import ThreatAnalysis from './pages/ThreatAnalysis';
import SoupUpdates from './pages/SoupUpdates';
import Reports from './pages/Reports';
import SystemStatus from './pages/SystemStatus';
import { Toaster } from './components/ui/toaster';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const apiBaseUrl = 'http://localhost:8000';

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard apiBaseUrl={apiBaseUrl} />;
      case 'logs':
        return <LogCollection apiBaseUrl={apiBaseUrl} />;
      case 'threats':
        return <ThreatAnalysis apiBaseUrl={apiBaseUrl} />;
      case 'soup':
        return <SoupUpdates apiBaseUrl={apiBaseUrl} />;
      case 'reports':
        return <Reports apiBaseUrl={apiBaseUrl} />;
      case 'system':
        return <SystemStatus apiBaseUrl={apiBaseUrl} />;
      default:
        return <Dashboard apiBaseUrl={apiBaseUrl} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Toaster />
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <main 
        className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? 'ml-20' : 'ml-[280px]'
        }`}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderView()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
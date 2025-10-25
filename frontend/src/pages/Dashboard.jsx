import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Database, AlertTriangle, Monitor, HardDrive } from 'lucide-react';
import toast from 'react-hot-toast';
import StatCard from '../components/dashboard/StatCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import ThreatChart from '../components/dashboard/ThreatChart';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { getHealth, getCollectionStatus } from '../utils/api';
import { mockSystemHealth, mockRecentActivity } from '../data/mockData';

const Dashboard = ({ apiBaseUrl }) => {
  const [healthData, setHealthData] = useState(mockSystemHealth);
  const [activities, setActivities] = useState(mockRecentActivity);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Loading dashboard data...');
    try {
      const health = await getHealth(apiBaseUrl);
      setHealthData(health);
      toast.success('Dashboard data loaded', { id: loadingToast });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data', { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const threatData = {
    critical: 15,
    high: 42,
    medium: 68,
    low: 17
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard Overview</h1>
          <p className="text-muted-foreground mt-1">Monitor your system's security posture</p>
        </div>
        <Button onClick={loadDashboardData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ staggerChildren: 0.1 }}
      >
        <StatCard
          title="Total Logs"
          value={healthData.database?.total_logs || 0}
          subtitle="Stored in database"
          icon={Database}
        />
        <StatCard
          title="Anomalies Detected"
          value={healthData.database?.anomalies || 0}
          subtitle="Threats identified"
          icon={AlertTriangle}
        />
        <StatCard
          title="Unique Hosts"
          value={healthData.database?.unique_hosts || 0}
          subtitle="Monitored systems"
          icon={Monitor}
        />
        <StatCard
          title="Database Size"
          value={healthData.database?.size_mb || 0}
          subtitle="MB"
          icon={HardDrive}
        />
      </motion.div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatChart data={threatData} />
        <ActivityFeed activities={activities} />
      </div>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center py-2 border-b border-border">
            <span className="text-muted-foreground">Deployment Mode:</span>
            <span className="font-medium text-foreground">{healthData.deployment_mode}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-border">
            <span className="text-muted-foreground">API Host:</span>
            <span className="font-medium text-foreground font-mono text-sm">{healthData.api_host}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-muted-foreground">AI Models:</span>
            <span className={`font-medium ${healthData.ai_models?.loaded ? 'text-command-green' : 'text-threat-red'}`}>
              {healthData.ai_models?.loaded ? '✓ Loaded' : '✗ Not Loaded'}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
import React, { useState, useEffect } from 'react';
import { RefreshCw, Server, Database, Brain, HardDrive, Shield, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { getHealth, getIsolationStatus } from '../utils/api';
import { mockSystemHealth, mockIsolationStatus } from '../data/mockData';
import { formatTimestamp, formatFileSize, formatDeploymentMode } from '../utils/formatters';

const SystemStatus = ({ apiBaseUrl }) => {
  const [healthData, setHealthData] = useState(mockSystemHealth);
  const [isolationData, setIsolationData] = useState(mockIsolationStatus);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSystemStatus();
  }, []);

  const loadSystemStatus = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Loading system status...');
    try {
      const health = await getHealth(apiBaseUrl);
      const isolation = await getIsolationStatus(apiBaseUrl);
      setHealthData(health);
      setIsolationData(isolation);
      toast.success('System status loaded', { id: loadingToast });
    } catch (error) {
      console.error('Failed to load system status:', error);
      toast.error('Failed to load system status', { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const severityMap = {
      'ok': 'low',
      'warning': 'medium',
      'error': 'critical'
    };
    return severityMap[status] || 'low';
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">System Status</h1>
          <p className="text-muted-foreground mt-1">Monitor system health and configuration</p>
        </div>
        <Button onClick={loadSystemStatus} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-primary" />
              <CardTitle>System Health</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Status:</span>
              <Badge variant={getStatusBadge(healthData.status)}>
                {healthData.status}
              </Badge>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Message:</span>
              <span className="text-sm text-foreground">{healthData.message}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Mode:</span>
              <span className="text-sm text-foreground font-mono">
                {formatDeploymentMode(healthData.deployment_mode)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">API Host:</span>
              <span className="text-sm text-foreground font-mono">{healthData.api_host}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-primary" />
              <CardTitle>Isolation Status</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Level:</span>
              <Badge variant={isolationData.report?.compliant ? 'default' : 'destructive'}>
                {isolationData.report?.isolation_level}
              </Badge>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Compliant:</span>
              <span className={`text-sm font-medium ${isolationData.report?.compliant ? 'text-command-green' : 'text-threat-red'}`}>
                {isolationData.report?.compliant ? '✓ Yes' : '✗ No'}
              </span>
            </div>
            {isolationData.report?.warnings?.length > 0 && (
              <div className="pt-2 border-t border-border">
                <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-hazard-yellow" />
                  Warnings
                </h4>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  {isolationData.report.warnings.map((warning, idx) => (
                    <li key={idx}>• {warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              <CardTitle>Database Statistics</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Total Logs:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.database?.total_logs?.toLocaleString() || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Unique Hosts:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.database?.unique_hosts || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Anomalies:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.database?.anomalies || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Size:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.database?.size_mb?.toFixed(2) || 0} MB
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              <CardTitle>AI Models</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Loaded:</span>
              <span className={`text-sm font-medium ${healthData.ai_models?.loaded ? 'text-command-green' : 'text-threat-red'}`}>
                {healthData.ai_models?.loaded ? '✓ Yes' : '✗ No'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Count:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.ai_models?.model_count || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Updated:</span>
              <span className="text-sm text-foreground font-mono text-xs">
                {formatTimestamp(healthData.ai_models?.last_updated)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <HardDrive className="w-5 h-5 text-primary" />
              <CardTitle>Temporary Storage</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Files:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.temp_storage?.files || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-muted-foreground">Size:</span>
              <span className="text-sm text-foreground font-semibold">
                {healthData.temp_storage?.size_mb?.toFixed(2) || 0} MB
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SystemStatus;
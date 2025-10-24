import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select } from '../components/ui/select';
import { Card, CardContent } from '../components/ui/card';
import ThreatCard from '../components/threats/ThreatCard';
import { runAnalysis } from '../utils/api';
import { mockThreats } from '../data/mockData';

const ThreatAnalysis = ({ apiBaseUrl }) => {
  const [threats, setThreats] = useState(mockThreats);
  const [loading, setLoading] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const handleRunAnalysis = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Running threat analysis...');
    try {
      const result = await runAnalysis(apiBaseUrl);
      if (result.top_threats) {
        setThreats(result.top_threats);
        toast.success(`Analysis complete: ${result.top_threats.length} threats found`, { id: loadingToast });
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('Analysis failed', { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const filteredThreats = threats.filter(threat => {
    const matchesSeverity = filterSeverity === 'all' || threat.severity === filterSeverity;
    const matchesType = filterType === 'all' || threat.detection_type === filterType;
    const matchesSearch = threat.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         threat.host.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesType && matchesSearch;
  });

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Threat Analysis</h1>
          <p className="text-muted-foreground mt-1">Analyze and investigate security threats</p>
        </div>
        <Button onClick={handleRunAnalysis} disabled={loading}>
          <Search className={`w-4 h-4 mr-2 ${loading ? 'animate-pulse' : ''}`} />
          Run Analysis
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Severity</label>
              <Select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Detection Type</label>
              <Select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                <option value="all">All Types</option>
                <option value="anomaly">Anomaly</option>
                <option value="rule">Rule</option>
                <option value="ioc">IoC</option>
                <option value="ttp">TTP</option>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search threats..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Threats</span>
              <span className="text-2xl font-bold text-foreground">{filteredThreats.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Critical</span>
              <span className="text-2xl font-bold text-severity-critical">
                {filteredThreats.filter(t => t.severity === 'critical').length}
              </span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">High</span>
              <span className="text-2xl font-bold text-severity-high">
                {filteredThreats.filter(t => t.severity === 'high').length}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Threat List */}
      <div className="space-y-4">
        {filteredThreats.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <p className="text-muted-foreground">No threats found</p>
            </CardContent>
          </Card>
        ) : (
          <motion.div
            className="space-y-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {filteredThreats.map((threat, index) => (
              <motion.div
                key={threat.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <ThreatCard threat={threat} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ThreatAnalysis;
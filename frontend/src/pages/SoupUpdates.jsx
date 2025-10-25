import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Upload, CheckCircle, XCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { applySoupUpdate, getSoupHistory } from '../utils/api';
import { mockSoupHistory } from '../data/mockData';
import { formatTimestamp } from '../utils/formatters';

const SoupUpdates = ({ apiBaseUrl }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState(mockSoupHistory);

  const handleApplyUpdate = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const loadingToast = toast.loading('Applying SOUP update...');
    try {
      const result = await applySoupUpdate(apiBaseUrl, selectedFile);
      toast.success(result.message, { id: loadingToast });
      setSelectedFile(null);
      // Refresh history
      const historyData = await getSoupHistory(apiBaseUrl);
      setHistory(historyData.updates);
    } catch (error) {
      toast.error(`Update failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">SOUP Updates</h1>
        <p className="text-muted-foreground mt-1">Secure Offline Update Protocol</p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Apply Update Package</CardTitle>
          <CardDescription>Upload and apply SOUP update packages to the system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            type="file"
            onChange={(e) => setSelectedFile(e.target.files[0])}
            accept=".soup"
          />
          {selectedFile && (
            <p className="text-sm text-muted-foreground">
              Selected: <span className="font-mono">{selectedFile.name}</span>
            </p>
          )}
          <Button 
            onClick={handleApplyUpdate} 
            disabled={!selectedFile || loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Apply Update
          </Button>
        </CardContent>
      </Card>

      {/* Update History */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-foreground">Update History</h2>
        <div className="space-y-3">
          {history.map((update, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="text-lg">
                        v{update.version}
                      </Badge>
                      <Badge variant={update.status === 'success' ? 'default' : 'destructive'}>
                        {update.status === 'success' ? (
                          <CheckCircle className="w-3 h-3 mr-1" />
                        ) : (
                          <XCircle className="w-3 h-3 mr-1" />
                        )}
                        {update.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      {formatTimestamp(update.timestamp)}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 font-mono">{update.package}</p>
                  {update.summary && (
                    <div className="space-y-2 text-sm">
                      {update.summary.models.length > 0 && (
                        <div className="flex gap-2">
                          <span className="text-muted-foreground">Models:</span>
                          <span className="text-foreground">{update.summary.models.join(', ')}</span>
                        </div>
                      )}
                      {update.summary.rules.length > 0 && (
                        <div className="flex gap-2">
                          <span className="text-muted-foreground">Rules:</span>
                          <span className="text-foreground">{update.summary.rules.join(', ')}</span>
                        </div>
                      )}
                      {update.summary.threat_intel.length > 0 && (
                        <div className="flex gap-2">
                          <span className="text-muted-foreground">Threat Intel:</span>
                          <span className="text-foreground">{update.summary.threat_intel.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SoupUpdates;
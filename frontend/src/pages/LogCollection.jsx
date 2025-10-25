import React, { useState } from 'react';
import { Upload, HardDrive, Lock, Usb, Search, Database } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from '../components/ui/dialog';
import { uploadLogs, collectLocal, collectSSH, collectUSB, parseLogs, storeLogs } from '../utils/api';

const LogCollection = ({ apiBaseUrl }) => {
  const [activeModal, setActiveModal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [sshForm, setSshForm] = useState({ host: '', username: '', password: '' });
  const [selectedFile, setSelectedFile] = useState(null);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const loadingToast = toast.loading('Uploading file...');
    try {
      const result = await uploadLogs(apiBaseUrl, selectedFile);
      toast.success(result.message, { id: loadingToast });
      setSelectedFile(null);
      setActiveModal(null);
    } catch (error) {
      toast.error(`Upload failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const handleCollectLocal = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Collecting local logs...');
    try {
      const result = await collectLocal(apiBaseUrl);
      toast.success(`Collected ${result.collected_files?.length || 0} files`, { id: loadingToast });
    } catch (error) {
      toast.error(`Collection failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const handleCollectSSH = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Connecting via SSH...');
    try {
      const result = await collectSSH(apiBaseUrl, sshForm.host, sshForm.username, sshForm.password);
      toast.success(result.message, { id: loadingToast });
      setActiveModal(null);
      setSshForm({ host: '', username: '', password: '' });
    } catch (error) {
      toast.error(`SSH collection failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const handleParseLogs = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Parsing logs...');
    try {
      const result = await parseLogs(apiBaseUrl);
      toast.success(`Parsed ${result.files_parsed} files`, { id: loadingToast });
    } catch (error) {
      toast.error(`Parsing failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const handleStoreLogs = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Storing logs...');
    try {
      const result = await storeLogs(apiBaseUrl);
      toast.success(`Stored ${result.total_rows} log entries`, { id: loadingToast });
    } catch (error) {
      toast.error(`Storage failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Log Collection</h1>
        <p className="text-muted-foreground mt-1">Collect and manage log files from various sources</p>
      </div>

      {/* Collection Methods Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setActiveModal('upload')}>
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <Upload className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>Upload Logs</CardTitle>
            <CardDescription>Upload log files from your local system</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              Upload Files
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <HardDrive className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>Collect Local</CardTitle>
            <CardDescription>Collect logs from the local system</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={handleCollectLocal} disabled={loading}>
              Collect Local Logs
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setActiveModal('ssh')}>
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <Lock className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>SSH Collection</CardTitle>
            <CardDescription>Collect logs from remote Linux servers</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              Configure SSH
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setActiveModal('usb')}>
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <Usb className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>USB Collection</CardTitle>
            <CardDescription>Collect logs from USB drives</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              Scan USB Drives
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Log Processing Section */}
      <Card>
        <CardHeader>
          <CardTitle>Log Processing</CardTitle>
          <CardDescription>Parse and store collected logs in the database</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button onClick={handleParseLogs} disabled={loading}>
              <Search className="w-4 h-4 mr-2" />
              Parse Logs
            </Button>
            <Button onClick={handleStoreLogs} disabled={loading}>
              <Database className="w-4 h-4 mr-2" />
              Store in Database
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Upload Modal */}
      <Dialog isOpen={activeModal === 'upload'} onClose={() => setActiveModal(null)}>
        <DialogClose onClose={() => setActiveModal(null)} />
        <DialogHeader>
          <DialogTitle>Upload Log Files</DialogTitle>
        </DialogHeader>
        <DialogContent>
          <div className="space-y-4">
            <Input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              accept=".log,.txt,.evtx,.json,.csv"
            />
            {selectedFile && (
              <p className="text-sm text-muted-foreground">Selected: {selectedFile.name}</p>
            )}
          </div>
        </DialogContent>
        <DialogFooter>
          <Button onClick={handleUpload} disabled={!selectedFile || loading}>
            Upload
          </Button>
          <Button variant="outline" onClick={() => setActiveModal(null)}>
            Cancel
          </Button>
        </DialogFooter>
      </Dialog>

      {/* SSH Modal */}
      <Dialog isOpen={activeModal === 'ssh'} onClose={() => setActiveModal(null)}>
        <DialogClose onClose={() => setActiveModal(null)} />
        <DialogHeader>
          <DialogTitle>SSH Collection</DialogTitle>
        </DialogHeader>
        <DialogContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Host</label>
              <Input
                type="text"
                value={sshForm.host}
                onChange={(e) => setSshForm({ ...sshForm, host: e.target.value })}
                placeholder="192.168.1.100"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Username</label>
              <Input
                type="text"
                value={sshForm.username}
                onChange={(e) => setSshForm({ ...sshForm, username: e.target.value })}
                placeholder="admin"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <Input
                type="password"
                value={sshForm.password}
                onChange={(e) => setSshForm({ ...sshForm, password: e.target.value })}
              />
            </div>
          </div>
        </DialogContent>
        <DialogFooter>
          <Button onClick={handleCollectSSH} disabled={loading}>
            Connect & Collect
          </Button>
          <Button variant="outline" onClick={() => setActiveModal(null)}>
            Cancel
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

export default LogCollection;
import React, { useState } from 'react';
import { FileSpreadsheet, FileText, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { exportCSV, exportPDF } from '../utils/api';

const Reports = ({ apiBaseUrl }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleExportCSV = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Exporting CSV report...');
    try {
      const blob = await exportCSV(apiBaseUrl);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `quorum-report-${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('CSV report exported successfully', { id: loadingToast });
    } catch (error) {
      toast.error(`Export failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Generating PDF report...');
    try {
      const blob = await exportPDF(apiBaseUrl);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `quorum-report-${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('PDF report exported successfully', { id: loadingToast });
    } catch (error) {
      toast.error(`Export failed: ${error.message}`, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Reports</h1>
        <p className="text-muted-foreground mt-1">Export analysis results and system reports</p>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <FileSpreadsheet className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>CSV Export</CardTitle>
            <CardDescription>
              Export threat analysis data in CSV format for further processing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleExportCSV} disabled={loading} className="w-full">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <CardTitle>PDF Report</CardTitle>
            <CardDescription>
              Generate comprehensive PDF report with charts and statistics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleExportPDF} disabled={loading} className="w-full">
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Report Contents Info */}
      <Card>
        <CardHeader>
          <CardTitle>Report Contents</CardTitle>
          <CardDescription>What's included in the exported reports</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              System health and statistics
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              Detected threats and anomalies
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              Severity distribution
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              Top threats with details
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              Collection and analysis timeline
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
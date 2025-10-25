// mockData.js
// Mock data for root component props
export const mockRootProps = {
  apiBaseUrl: 'http://localhost:8000'
};

// Mock system health data
export const mockSystemHealth = {
  status: 'ok',
  message: 'System is Running',
  deployment_mode: 'isolated',
  api_host: '127.0.0.1',
  database: {
    total_logs: 15847,
    unique_hosts: 23,
    anomalies: 142,
    size_mb: 245.8
  },
  temp_storage: {
    files: 5,
    size_mb: 12.3
  },
  ai_models: {
    loaded: true,
    model_count: 2,
    last_updated: '2025-01-15T10:30:00Z'
  }
};

// Mock isolation status
export const mockIsolationStatus = {
  status: 'ok',
  report: {
    isolation_level: 'fully_isolated',
    compliant: true,
    warnings: []
  }
};

// Mock threat data
export const mockThreats = [
  {
    id: 'threat-1',
    timestamp: '2025-01-20T14:23:45Z',
    host: 'web-server-01',
    severity: 'critical',
    detection_type: 'ioc',
    score: 0.9876,
    message: 'Malicious IP connection attempt detected from 192.168.1.100',
    details: {
      indicator: '192.168.1.100',
      indicator_type: 'ip_address',
      threat_intel_match: true
    }
  },
  {
    id: 'threat-2',
    timestamp: '2025-01-20T14:15:32Z',
    host: 'db-server-03',
    severity: 'high',
    detection_type: 'ttp',
    score: 0.8543,
    message: 'Suspicious PowerShell execution detected - potential credential dumping',
    details: {
      ttp_id: 'T1003',
      tactic: 'Credential Access',
      technique: 'OS Credential Dumping',
      process: 'powershell.exe'
    }
  },
  // ... existing code ...
];

// Mock log collection status
export const mockCollectionStatus = {
  status: 'operational',
  system: 'Windows',
  temp_storage: {
    files: 8,
    size_mb: 15.7
  },
  database: {
    total_logs: 15847,
    unique_hosts: 23,
    anomalies: 142
  }
};

// Mock recent activity
export const mockRecentActivity = [
  {
    id: 'activity-1',
    timestamp: '2025-01-20T14:30:00Z',
    type: 'analysis',
    message: 'Comprehensive analysis completed - 142 threats found',
    status: 'success'
  },
  // ... existing code ...
];

// Mock SOUP update history
export const mockSoupHistory = [
  {
    timestamp: '2025-01-15T10:00:00Z',
    version: '2.1.0',
    package: 'quorum-update-2.1.0.soup',
    status: 'success',
    summary: {
      models: ['iforest_model_v2.pkl', 'tfidf_vectorizer_v2.pkl'],
      rules: ['brute_force_detection.json'],
      threat_intel: ['indicators_jan2025.json']
    }
  },
  // ... existing code ...
];

// Mock USB drives
export const mockUsbDrives = [
  {
    mount_point: 'D:\\',
    name: 'USB_DRIVE_1',
    exists: true
  },
  {
    mount_point: 'E:\\',
    name: 'BACKUP_DISK',
    exists: true
  }
];
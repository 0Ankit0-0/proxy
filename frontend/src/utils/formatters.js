// formatters.js
// Format timestamp to readable string
export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// Format relative time (e.g., "5m ago", "2h ago")
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

// Format file size in bytes to human readable
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
};

// Format number with commas
export const formatNumber = (num) => {
  return num.toLocaleString('en-US');
};

// Format percentage
export const formatPercentage = (value, total) => {
  if (total === 0) return '0%';
  return `${((value / total) * 100).toFixed(1)}%`;
};

// Format severity level
export const formatSeverity = (severity) => {
  const map = {
    'critical': 'Critical',
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low'
  };
  return map[severity] || severity;
};

// Format detection type
export const formatDetectionType = (type) => {
  const map = {
    'anomaly': 'Anomaly Detection',
    'rule': 'Rule Match',
    'ioc': 'IoC Match',
    'ttp': 'TTP Detection'
  };
  return map[type] || type;
};

// Format deployment mode
export const formatDeploymentMode = (mode) => {
  const map = {
    'isolated': 'Isolated (Localhost Only)',
    'lan': 'LAN Mode (Private Network)',
    'debug': 'Debug Mode (Development)'
  };
  return map[mode] || mode;
};

// Format collection source
export const formatCollectionSource = (source) => {
  const map = {
    'upload': 'File Upload',
    'local': 'Local System',
    'ssh': 'SSH (Remote Linux)',
    'winrm': 'WinRM (Remote Windows)',
    'usb': 'USB Drive',
    'network': 'Network Share',
    'directory': 'Directory'
  };
  return map[source] || source;
};

// Format score to 4 decimal places
export const formatScore = (score) => {
  return score.toFixed(4);
};

// Truncate text to max length
export const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};
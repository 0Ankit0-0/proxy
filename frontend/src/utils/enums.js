// enums.js
// Severity levels for threats
export const ThreatSeverity = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
};

// Detection types
export const DetectionType = {
  ANOMALY: 'anomaly',
  RULE: 'rule',
  IOC: 'ioc',
  TTP: 'ttp'
};

// Deployment modes
export const DeploymentMode = {
  ISOLATED: 'isolated',
  LAN: 'lan',
  DEBUG: 'debug'
};

// Log collection sources
export const CollectionSource = {
  UPLOAD: 'upload',
  LOCAL: 'local',
  SSH: 'ssh',
  WINRM: 'winrm',
  USB: 'usb',
  NETWORK: 'network',
  DIRECTORY: 'directory'
};

// Query types
export const QueryType = {
  GET_ANOMALIES: 'get_anomalies',
  GET_RECENT: 'get_recent',
  COUNT_BY_HOST: 'count_by_host'
};

// Status types
export const StatusType = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  LOADING: 'loading'
};

// Update status
export const UpdateStatus = {
  SUCCESS: 'success',
  FAILED: 'failed',
  PENDING: 'pending'
};
// api.js
/**
 * API endpoint functions for fetching data from the backend
 * All functions return Promises
 */

/**
 * Health check endpoints
 */
export const getHealth = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/health/`);
  return response.json();
};

export const getIsolationStatus = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/health/isolation`);
  return response.json();
};

/**
 * Log collection endpoints
 */
export const uploadLogs = async (apiBaseUrl, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${apiBaseUrl}/logs/upload`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};

export const collectLocal = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/collect`, {
    method: 'POST'
  });
  return response.json();
};

export const collectSSH = async (apiBaseUrl, host, username, password, remotePaths = null) => {
  const response = await fetch(`${apiBaseUrl}/logs/collect/ssh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, username, password, remote_paths: remotePaths })
  });
  return response.json();
};

export const collectWinRM = async (apiBaseUrl, host, username, password, remotePaths = null) => {
  const response = await fetch(`${apiBaseUrl}/logs/collect/winrm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, username, password, remote_paths: remotePaths })
  });
  return response.json();
};

export const collectUSB = async (apiBaseUrl, autoDetect = true, mountPoint = null) => {
  const response = await fetch(`${apiBaseUrl}/logs/collect/usb?auto_detect=${autoDetect}${mountPoint ? `&mount_point=${mountPoint}` : ''}`, {
    method: 'POST'
  });
  return response.json();
};

export const detectUSB = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/collect/usb/detect`);
  return response.json();
};

export const getCollectionStatus = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/status`);
  return response.json();
};

/**
 * Log management endpoints
 */
export const parseLogs = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/parse`, {
    method: 'POST'
  });
  return response.json();
};

export const storeLogs = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/store`, {
    method: 'POST'
  });
  return response.json();
};

export const queryLogs = async (apiBaseUrl, queryName, limit = 100) => {
  const response = await fetch(`${apiBaseUrl}/logs/query/${queryName}?limit=${limit}`);
  return response.json();
};

export const clearTemp = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/logs/clear`, {
    method: 'DELETE'
  });
  return response.json();
};

/**
 * Analysis endpoints
 */
export const runAnalysis = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/analysis/comprehensive`, {
    method: 'POST'
  });
  return response.json();
};

/**
 * SOUP endpoints
 */
export const applySoupUpdate = async (apiBaseUrl, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${apiBaseUrl}/soup/update`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};

export const getSoupStatus = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/soup/status`);
  return response.json();
};

export const getSoupHistory = async (apiBaseUrl, limit = 10) => {
  const response = await fetch(`${apiBaseUrl}/soup/history?limit=${limit}`);
  return response.json();
};

/**
 * Report endpoints
 */
export const exportCSV = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/reports/export/csv`);
  return response.blob();
};

export const exportPDF = async (apiBaseUrl) => {
  const response = await fetch(`${apiBaseUrl}/reports/export/pdf`);
  return response.blob();
};
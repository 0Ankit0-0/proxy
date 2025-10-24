import React from 'react';
import styles from './Badge.module.css';

const Badge = ({ children, severity = 'low', className = '' }) => {
  return (
    <span className={`${styles.badge} ${styles[severity]} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;
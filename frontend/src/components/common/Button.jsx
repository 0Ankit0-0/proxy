import React from 'react';
import styles from './Button.module.css';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = ''
}) => {
  const buttonClass = `${styles.button} ${styles[variant]} ${styles[size]} ${className}`;
  
  return (
    <button
      type={type}
      className={buttonClass}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? <span className={styles.spinner}></span> : children}
    </button>
  );
};

export default Button;
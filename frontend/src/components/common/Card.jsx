import React from 'react';
import styles from './Card.module.css';

const Card = ({ children, title, className = '', hover = false }) => {
  return (
    <div className={`${styles.card} ${hover ? styles.hover : ''} ${className}`}>
      {title && <div className={styles.title}>{title}</div>}
      <div className={styles.content}>{children}</div>
    </div>
  );
};

export default Card;
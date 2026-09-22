import React from 'react';
import styles from './Input.module.css';
import { clsx } from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, fullWidth = true, ...props }, ref) => {
    return (
      <div className={clsx(styles.wrapper, fullWidth && styles.fullWidth)}>
        {label && (
          <label className={styles.label}>
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            styles.input,
            error && styles.errorInput,
            className
          )}
          {...props}
        />
        {error && <span className={styles.errorMessage}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';

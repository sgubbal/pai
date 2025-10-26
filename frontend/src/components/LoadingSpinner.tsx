import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  text,
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-3">
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 dark:border-gray-700 border-t-primary-600 rounded-full animate-spin`}
      />
      {text && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
};

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full mb-4 justify-start">
      <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-2xl px-5 py-4">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full loading-dot"></div>
          <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full loading-dot"></div>
          <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full loading-dot"></div>
        </div>
      </div>
    </div>
  );
};

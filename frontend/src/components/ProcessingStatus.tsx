'use client';

import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';

interface ProcessingStatusProps {
  status: {
    isProcessing: boolean;
    currentStep: string;
    progress: number;
  };
}

export default function ProcessingStatus({ status }: ProcessingStatusProps) {
  if (!status.isProcessing && !status.currentStep) {
    return null;
  }

  const getStatusIcon = () => {
    if (status.isProcessing) {
      return <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />;
    } else if (status.progress === 100) {
      return <CheckCircle className="w-5 h-5 text-success-600" />;
    } else {
      return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    if (status.isProcessing) {
      return 'text-primary-600';
    } else if (status.progress === 100) {
      return 'text-success-600';
    } else {
      return 'text-gray-600';
    }
  };

  const getProgressBarColor = () => {
    if (status.progress === 100) {
      return 'bg-success-600';
    } else if (status.progress > 0) {
      return 'bg-primary-600';
    } else {
      return 'bg-gray-300';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-3">
        {getStatusIcon()}
        <h2 className="text-lg font-semibold text-gray-900">Processing Status</h2>
      </div>

      <div className="space-y-3">
        {/* Current Step */}
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {status.currentStep || 'Ready'}
          </span>
          <span className="text-sm text-gray-500">
            {status.progress}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="progress-bar">
          <div
            className={`progress-bar-fill ${getProgressBarColor()}`}
            style={{ width: `${status.progress}%` }}
          ></div>
        </div>

        {/* Processing Steps */}
        <div className="space-y-2 mt-4">
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`w-3 h-3 rounded-full ${
                status.progress >= 10 ? 'bg-success-600' : 'bg-gray-300'
              }`}
            ></div>
            <span className={status.progress >= 10 ? 'text-gray-700' : 'text-gray-400'}>
              Upload Documents
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`w-3 h-3 rounded-full ${
                status.progress >= 30 ? 'bg-success-600' : 'bg-gray-300'
              }`}
            ></div>
            <span className={status.progress >= 30 ? 'text-gray-700' : 'text-gray-400'}>
              Extract Text & Classify
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`w-3 h-3 rounded-full ${
                status.progress >= 60 ? 'bg-success-600' : 'bg-gray-300'
              }`}
            ></div>
            <span className={status.progress >= 60 ? 'text-gray-700' : 'text-gray-400'}>
              AI Data Extraction
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`w-3 h-3 rounded-full ${
                status.progress >= 80 ? 'bg-success-600' : 'bg-gray-300'
              }`}
            ></div>
            <span className={status.progress >= 80 ? 'text-gray-700' : 'text-gray-400'}>
              Field Mapping
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`w-3 h-3 rounded-full ${
                status.progress >= 100 ? 'bg-success-600' : 'bg-gray-300'
              }`}
            ></div>
            <span className={status.progress >= 100 ? 'text-gray-700' : 'text-gray-400'}>
              Complete
            </span>
          </div>
        </div>

        {/* Estimated Time */}
        {status.isProcessing && status.progress > 0 && status.progress < 100 && (
          <div className="mt-4 p-2 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-2 text-xs text-blue-700">
              <AlertCircle className="w-3 h-3" />
              <span>
                Estimated time remaining: {Math.ceil((100 - status.progress) / 10)} seconds
              </span>
            </div>
          </div>
        )}

        {/* Completion Message */}
        {status.progress === 100 && !status.isProcessing && (
          <div className="mt-4 p-3 bg-success-50 rounded-lg">
            <div className="flex items-center space-x-2 text-sm text-success-700">
              <CheckCircle className="w-4 h-4" />
              <span>Processing completed successfully!</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

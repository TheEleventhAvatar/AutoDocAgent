'use client';

import { useState } from 'react';
import DocumentUpload from '@/components/DocumentUpload';
import DataPreview from '@/components/DataPreview';
import TemplateSelector from '@/components/TemplateSelector';
import ProcessingStatus from '@/components/ProcessingStatus';
import ResultsDisplay from '@/components/ResultsDisplay';
import { toast } from 'react-toastify';

export default function HomePage() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [processingStatus, setProcessingStatus] = useState<{
    isProcessing: boolean;
    currentStep: string;
    progress: number;
  }>({
    isProcessing: false,
    currentStep: '',
    progress: 0,
  });
  const [results, setResults] = useState<any>(null);

  const handleFilesUploaded = async (files: File[]) => {
    setUploadedFiles(files);
    setExtractedData(null);
    setResults(null);
    
    try {
      setProcessingStatus({
        isProcessing: true,
        currentStep: 'Uploading files...',
        progress: 10,
      });

      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const uploadResult = await response.json();
      toast.success(`Successfully uploaded ${uploadResult.files.length} files`);
      
      // Auto-extract data after upload
      await handleExtractData(uploadResult.files);
      
    } catch (error) {
      toast.error('Upload failed: ' + (error as Error).message);
      setProcessingStatus({ isProcessing: false, currentStep: '', progress: 0 });
    }
  };

  const handleExtractData = async (filePaths: string[]) => {
    try {
      setProcessingStatus({
        isProcessing: true,
        currentStep: 'Extracting text from documents...',
        progress: 30,
      });

      // Process batch documents
      const response = await fetch('/api/process-batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_paths: filePaths }),
      });

      if (!response.ok) {
        throw new Error('Data extraction failed');
      }

      const data = await response.json();
      setExtractedData(data);
      
      setProcessingStatus({
        isProcessing: false,
        currentStep: 'Data extraction completed',
        progress: 100,
      });

      toast.success('Data extracted successfully');
      
      // Reset processing status after delay
      setTimeout(() => {
        setProcessingStatus({ isProcessing: false, currentStep: '', progress: 0 });
      }, 2000);
      
    } catch (error) {
      toast.error('Data extraction failed: ' + (error as Error).message);
      setProcessingStatus({ isProcessing: false, currentStep: '', progress: 0 });
    }
  };

  const handleTemplateSelect = (templatePath: string) => {
    setSelectedTemplate(templatePath);
  };

  const handleFillForm = async () => {
    if (!selectedTemplate || !extractedData) {
      toast.error('Please select a template and ensure data is extracted');
      return;
    }

    try {
      setProcessingStatus({
        isProcessing: true,
        currentStep: 'Filling form template...',
        progress: 50,
      });

      const response = await fetch('/api/fill-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_path: selectedTemplate,
          data: extractedData.merged_fields,
        }),
      });

      if (!response.ok) {
        throw new Error('Form filling failed');
      }

      const result = await response.json();
      setResults(result);
      
      setProcessingStatus({
        isProcessing: false,
        currentStep: 'Form filled successfully',
        progress: 100,
      });

      toast.success('Form filled successfully');
      
    } catch (error) {
      toast.error('Form filling failed: ' + (error as Error).message);
      setProcessingStatus({ isProcessing: false, currentStep: '', progress: 0 });
    }
  };

  const handleAutonomousProcess = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Please upload documents first');
      return;
    }

    try {
      setProcessingStatus({
        isProcessing: true,
        currentStep: 'Starting autonomous processing...',
        progress: 10,
      });

      // Get file paths from uploaded files
      const filePaths = uploadedFiles.map(file => `../uploads/${file.name}`);

      const response = await fetch('/api/autonomous-process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_paths: filePaths }),
      });

      if (!response.ok) {
        throw new Error('Autonomous processing failed');
      }

      const result = await response.json();
      setResults(result);
      
      setProcessingStatus({
        isProcessing: false,
        currentStep: 'Autonomous processing completed',
        progress: 100,
      });

      if (result.status === 'completed') {
        toast.success(`Successfully filled ${result.filled_templates} templates`);
      } else {
        toast.error('Processing completed with some errors');
      }
      
    } catch (error) {
      toast.error('Autonomous processing failed: ' + (error as Error).message);
      setProcessingStatus({ isProcessing: false, currentStep: '', progress: 0 });
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const response = await fetch(`/api/download/${filename}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success('File downloaded successfully');
    } catch (error) {
      toast.error('Download failed: ' + (error as Error).message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AutoDoc Agent</h1>
                <p className="text-sm text-gray-500">AI-Powered Document Automation</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={handleAutonomousProcess}
                disabled={uploadedFiles.length === 0 || processingStatus.isProcessing}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Auto Process</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Upload and Processing */}
          <div className="lg:col-span-1 space-y-6">
            <DocumentUpload 
              onFilesUploaded={handleFilesUploaded}
              isProcessing={processingStatus.isProcessing}
            />
            
            <ProcessingStatus 
              status={processingStatus}
            />
          </div>

          {/* Middle Column - Data Preview */}
          <div className="lg:col-span-1">
            <DataPreview 
              data={extractedData}
              files={uploadedFiles}
            />
          </div>

          {/* Right Column - Templates and Results */}
          <div className="lg:col-span-1 space-y-6">
            <TemplateSelector 
              onTemplateSelect={handleTemplateSelect}
              selectedTemplate={selectedTemplate}
            />
            
            {selectedTemplate && extractedData && (
              <div className="card">
                <button
                  onClick={handleFillForm}
                  disabled={processingStatus.isProcessing}
                  className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Fill Selected Template
                </button>
              </div>
            )}
            
            <ResultsDisplay 
              results={results}
              onDownload={handleDownload}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

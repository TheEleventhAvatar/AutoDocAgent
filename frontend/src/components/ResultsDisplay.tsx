'use client';

import { useState } from 'react';
import { Download, FileText, CheckCircle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';

interface ResultsDisplayProps {
  results: any;
  onDownload: (filename: string) => void;
}

export default function ResultsDisplay({ results, onDownload }: ResultsDisplayProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  if (!results) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Results</h2>
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No results yet</p>
          <p className="text-sm mt-2">Process documents to see results</p>
        </div>
      </div>
    );
  }

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-error-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600';
      case 'failed':
        return 'text-error-600';
      default:
        return 'text-gray-600';
    }
  };

  // Handle different result formats
  if (results.status === 'completed' && results.filled_documents) {
    // Autonomous processing results
    return (
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          {getStatusIcon(results.status)}
          <h2 className="text-lg font-semibold text-gray-900">Processing Results</h2>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-600">Documents Processed</p>
            <p className="text-lg font-semibold text-gray-900">{results.processed_documents}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-600">Templates Filled</p>
            <p className="text-lg font-semibold text-gray-900">{results.filled_templates}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-600">Fields Extracted</p>
            <p className="text-lg font-semibold text-gray-900">{results.extracted_data?.total_fields_extracted || 0}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-600">Success Rate</p>
            <p className="text-lg font-semibold text-gray-900">
              {results.filled_templates > 0 ? '100%' : '0%'}
            </p>
          </div>
        </div>

        {/* Filled Documents */}
        {results.filled_documents && results.filled_documents.length > 0 && (
          <div className="mb-4">
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => toggleSection('filled-docs')}
            >
              <h3 className="text-sm font-medium text-gray-700">Filled Documents</h3>
              {expandedSections.has('filled-docs') ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )}
            </div>
            
            {expandedSections.has('filled-docs') && (
              <div className="mt-3 space-y-2">
                {results.filled_documents.map((doc: any, index: number) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{doc.template_name}</p>
                        <p className="text-xs text-gray-500">{doc.template_type}</p>
                      </div>
                      {doc.output_path && (
                        <button
                          onClick={() => onDownload(doc.output_path.split('/').pop() || doc.template_name)}
                          className="btn-secondary text-xs px-3 py-1 flex items-center space-x-1"
                        >
                          <Download className="w-3 h-3" />
                          <span>Download</span>
                        </button>
                      )}
                    </div>
                    {doc.error && (
                      <div className="mt-2 text-xs text-error-600">
                        Error: {doc.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Missing Fields */}
        {results.missing_fields && (
          <div className="mb-4">
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => toggleSection('missing-fields')}
            >
              <h3 className="text-sm font-medium text-gray-700">Missing Fields Analysis</h3>
              {expandedSections.has('missing-fields') ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )}
            </div>
            
            {expandedSections.has('missing-fields') && (
              <div className="mt-3 space-y-3">
                {/* Summary */}
                <div className="p-3 bg-amber-50 rounded-lg">
                  <h4 className="text-sm font-medium text-amber-900 mb-2">Summary</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs text-amber-700">
                    <div>Fully fillable: {results.missing_fields.summary?.fully_fillable || 0}</div>
                    <div>Partially fillable: {results.missing_fields.summary?.partially_fillable || 0}</div>
                    <div>Missing required: {results.missing_fields.summary?.total_missing_required || 0}</div>
                    <div>Missing optional: {results.missing_fields.summary?.total_missing_optional || 0}</div>
                  </div>
                </div>

                {/* Prioritized Missing Fields */}
                {results.missing_fields.prioritized_missing_fields && results.missing_fields.prioritized_missing_fields.length > 0 && (
                  <div className="p-3 bg-red-50 rounded-lg">
                    <h4 className="text-sm font-medium text-red-900 mb-2">Critical Missing Fields</h4>
                    <div className="space-y-1">
                      {results.missing_fields.prioritized_missing_fields.slice(0, 5).map(([field, count]: [string, number], index: number) => (
                        <div key={index} className="flex justify-between text-xs text-red-700">
                          <span>{field}</span>
                          <span>needed for {count} templates</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {results.missing_fields.suggestions && results.missing_fields.suggestions.length > 0 && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">Suggestions</h4>
                    <ul className="space-y-1">
                      {results.missing_fields.suggestions.map((suggestion: string, index: number) => (
                        <li key={index} className="text-xs text-blue-700">
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Single template filling results
  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-4">
        {results.output_path ? (
          <CheckCircle className="w-5 h-5 text-success-600" />
        ) : (
          <AlertCircle className="w-5 h-5 text-error-600" />
        )}
        <h2 className="text-lg font-semibold text-gray-900">Form Filling Results</h2>
      </div>

      {results.output_path ? (
        <div className="space-y-4">
          <div className="p-3 bg-success-50 rounded-lg">
            <p className="text-sm text-success-700 font-medium">Form filled successfully!</p>
          </div>

          {/* Mapped Fields */}
          {results.mapped_fields && Object.keys(results.mapped_fields).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Mapped Fields</h3>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {Object.entries(results.mapped_fields).map(([templateField, value]: [string, any]) => (
                  <div key={templateField} className="flex justify-between text-xs p-2 bg-gray-50 rounded">
                    <span className="font-medium text-gray-700">{templateField}:</span>
                    <span className="text-gray-600 truncate ml-2">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Download Button */}
          <button
            onClick={() => onDownload(results.output_path.split('/').pop() || 'filled_form.pdf')}
            className="w-full btn-success flex items-center justify-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Filled Form</span>
          </button>
        </div>
      ) : (
        <div className="p-3 bg-error-50 rounded-lg">
          <p className="text-sm text-error-700">Form filling failed. Please check the template and try again.</p>
        </div>
      )}
    </div>
  );
}

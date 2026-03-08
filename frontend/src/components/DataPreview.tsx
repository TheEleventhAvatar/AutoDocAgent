'use client';

import { useState } from 'react';
import { Eye, EyeOff, FileText, User, Calendar, MapPin, Phone, Mail, CreditCard } from 'lucide-react';

interface DataPreviewProps {
  data: any;
  files: File[];
}

export default function DataPreview({ data, files }: DataPreviewProps) {
  const [showRawText, setShowRawText] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<number | null>(null);

  if (!data) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Extracted Data</h2>
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No data extracted yet</p>
          <p className="text-sm mt-2">Upload documents to see extracted information</p>
        </div>
      </div>
    );
  }

  const getFieldIcon = (fieldName: string) => {
    const field = fieldName.toLowerCase();
    if (field.includes('name') || field.includes('full')) return User;
    if (field.includes('date') || field.includes('birth')) return Calendar;
    if (field.includes('address') || field.includes('location')) return MapPin;
    if (field.includes('phone') || field.includes('mobile')) return Phone;
    if (field.includes('email') || field.includes('mail')) return Mail;
    if (field.includes('pan') || field.includes('aadhar') || field.includes('account')) return CreditCard;
    return FileText;
  };

  const formatFieldName = (fieldName: string) => {
    return fieldName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getDocumentTypeInfo = (type: string) => {
    const typeColors: { [key: string]: string } = {
      'invoice': 'bg-blue-100 text-blue-800',
      'resume': 'bg-green-100 text-green-800',
      'kyc': 'bg-purple-100 text-purple-800',
      'bank_statement': 'bg-yellow-100 text-yellow-800',
      'id_card': 'bg-red-100 text-red-800',
      'passport': 'bg-indigo-100 text-indigo-800',
      'general': 'bg-gray-100 text-gray-800'
    };
    
    return typeColors[type] || typeColors['general'];
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Extracted Data</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>{data.total_fields_extracted} fields</span>
          <span>•</span>
          <span>{data.document_count} documents</span>
        </div>
      </div>

      {/* Document Types Summary */}
      {data.document_info && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Document Types</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(
              data.document_info.reduce((acc: any, doc: any) => {
                acc[doc.type] = (acc[doc.type] || 0) + 1;
                return acc;
              }, {})
            ).map(([type, count]) => (
              <span
                key={type}
                className={`px-2 py-1 rounded-full text-xs font-medium ${getDocumentTypeInfo(type)}`}
              >
                {type} ({count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Fields */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Merged Data</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {Object.entries(data.merged_fields).map(([key, value]) => {
            const Icon = getFieldIcon(key);
            return (
              <div
                key={key}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <Icon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700">
                      {formatFieldName(key)}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {String(value)}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Document Details */}
      {data.document_info && data.document_info.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Document Details</h3>
          <div className="space-y-2">
            {data.document_info.map((doc: any, index: number) => (
              <div
                key={index}
                className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => setSelectedDocument(selectedDocument === index ? null : index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700">
                      {doc.file_path.split('/').pop()}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDocumentTypeInfo(doc.type)}`}>
                      {doc.type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {doc.extracted_fields?.length || 0} fields
                    </span>
                  </div>
                </div>
                
                {selectedDocument === index && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="text-xs text-gray-600 space-y-1">
                      <p>Text length: {doc.text_length?.toLocaleString()} characters</p>
                      {doc.extracted_fields && (
                        <div>
                          <p className="font-medium">Extracted fields:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {doc.extracted_fields.map((field: string, fIndex: number) => (
                              <span key={fIndex} className="px-1 py-0.5 bg-gray-200 rounded text-xs">
                                {field}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Toggle Raw Text */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={() => setShowRawText(!showRawText)}
          className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          {showRawText ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          <span>{showRawText ? 'Hide' : 'Show'} Raw Text</span>
        </button>
        
        {showRawText && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg max-h-40 overflow-y-auto">
            <pre className="text-xs text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(data.merged_fields, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { FileText, Download, Check } from 'lucide-react';

interface Template {
  name: string;
  path: string;
  type: string;
  fields?: string[];
  has_form_fields?: boolean;
}

interface TemplateSelectorProps {
  onTemplateSelect: (templatePath: string) => void;
  selectedTemplate: string;
}

export default function TemplateSelector({ onTemplateSelect, selectedTemplate }: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTemplateIcon = (type: string) => {
    switch (type) {
      case '.pdf':
        return <FileText className="w-5 h-5 text-red-500" />;
      case '.xlsx':
      case '.xls':
        return <FileText className="w-5 h-5 text-green-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTemplateTypeLabel = (type: string) => {
    switch (type) {
      case '.pdf':
        return 'PDF Form';
      case '.xlsx':
      case '.xls':
        return 'Excel Template';
      default:
        return 'Document';
    }
  };

  const getTemplateDescription = (template: Template) => {
    const name = template.name.toLowerCase();
    
    if (name.includes('kyc')) return 'Know Your Customer form';
    if (name.includes('hr') || name.includes('onboarding')) return 'Employee onboarding form';
    if (name.includes('tax')) return 'Tax declaration form';
    if (name.includes('bank') || name.includes('account')) return 'Bank account form';
    if (name.includes('invoice')) return 'Invoice template';
    if (name.includes('resume')) return 'Resume template';
    
    return 'Form template';
  };

  if (loading) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Form Templates</h2>
        <div className="text-center py-8">
          <div className="spinner w-8 h-8 mx-auto mb-3"></div>
          <p className="text-gray-500">Loading templates...</p>
        </div>
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Form Templates</h2>
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No templates found</p>
          <p className="text-sm mt-2">Add templates to the sample_templates directory</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Form Templates</h2>
      
      <div className="space-y-3">
        {templates.map((template) => {
          const isSelected = selectedTemplate === template.path;
          const description = getTemplateDescription(template);
          
          return (
            <div
              key={template.path}
              className={`p-3 border rounded-lg cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => onTemplateSelect(template.path)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex-shrink-0 mt-0.5">
                    {getTemplateIcon(template.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {template.name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {description}
                    </p>
                    <div className="flex items-center space-x-3 mt-2">
                      <span className="text-xs text-gray-400">
                        {getTemplateTypeLabel(template.type)}
                      </span>
                      {template.fields && (
                        <span className="text-xs text-gray-400">
                          {template.fields.length} fields
                        </span>
                      )}
                      {template.has_form_fields && (
                        <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">
                          Fillable
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex-shrink-0 ml-2">
                  {isSelected ? (
                    <div className="w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  ) : (
                    <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  )}
                </div>
              </div>
              
              {/* Show field preview if selected */}
              {isSelected && template.fields && template.fields.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs font-medium text-gray-700 mb-2">Template Fields:</p>
                  <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                    {template.fields.slice(0, 10).map((field, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600"
                      >
                        {field}
                      </span>
                    ))}
                    {template.fields.length > 10 && (
                      <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
                        +{template.fields.length - 10} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Instructions */}
      <div className="mt-4 p-3 bg-amber-50 rounded-lg">
        <h4 className="text-sm font-medium text-amber-900 mb-2">Template Selection:</h4>
        <ul className="text-xs text-amber-700 space-y-1">
          <li>• Select a template to fill with extracted data</li>
          <li>• Templates with form fields work best</li>
          <li>• Use "Auto Process" to fill all compatible templates</li>
          <li>• Missing fields will be highlighted in the results</li>
        </ul>
      </div>
    </div>
  );
}

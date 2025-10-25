import React, { useState } from 'react';
import { Download, Trash2 } from 'lucide-react';

interface JSONTemplateGeneratorProps {
  className?: string;
}

const JSONTemplateGenerator: React.FC<JSONTemplateGeneratorProps> = ({ className = '' }) => {
  const [template, setTemplate] = useState({
    name: '',
    description: '',
    organization: '',
    reporting_period: '',
    document_type: 'sustainability_document',
    sustainability_metrics: {
      carbon_footprint: 0,
      energy_consumption: 0,
      waste_reduction: 0,
      renewable_energy_percentage: 0
    }
  });

  const documentTypes = [
    'sustainability_document',
    'carbon_report', 
    'energy_audit',
    'waste_management',
    'green_certification'
  ];

  const updateTemplate = (field: string, value: any) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setTemplate(prev => ({
        ...prev,
        [parent]: {
          ...(prev[parent as keyof typeof prev] as any),
          [child]: value
        }
      }));
    } else {
      setTemplate(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const downloadTemplate = () => {
    const dataStr = JSON.stringify(template, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${template.name.toLowerCase().replace(/\s+/g, '-')}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const resetTemplate = () => {
    setTemplate({
      name: '',
      description: '',
      organization: '',
      reporting_period: '',
      document_type: 'sustainability_document',
      sustainability_metrics: {
        carbon_footprint: 0,
        energy_consumption: 0,
        waste_reduction: 0,
        renewable_energy_percentage: 0
      }
    });
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          🛠️ Create Custom JSON Template
        </h3>
        <p className="text-sm text-gray-600">
          Build your own sustainability document template
        </p>
      </div>

      <div className="space-y-4">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document Name
            </label>
            <input
              type="text"
              value={template.name}
              onChange={(e) => updateTemplate('name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g., Annual Sustainability Report"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Organization
            </label>
            <input
              type="text"
              value={template.organization}
              onChange={(e) => updateTemplate('organization', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g., Your Company Inc."
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={template.description}
            onChange={(e) => updateTemplate('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            rows={2}
            placeholder="Brief description of your sustainability document"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document Type
            </label>
            <select
              value={template.document_type}
              onChange={(e) => updateTemplate('document_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {documentTypes.map(type => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reporting Period
            </label>
            <input
              type="text"
              value={template.reporting_period}
              onChange={(e) => updateTemplate('reporting_period', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g., 2024, Q4 2024"
            />
          </div>
        </div>

        {/* Sustainability Metrics */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sustainability Metrics
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                Carbon Footprint (kg CO2)
              </label>
              <input
                type="number"
                value={template.sustainability_metrics.carbon_footprint}
                onChange={(e) => updateTemplate('sustainability_metrics.carbon_footprint', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="150.5"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                Energy Consumption (kWh)
              </label>
              <input
                type="number"
                value={template.sustainability_metrics.energy_consumption}
                onChange={(e) => updateTemplate('sustainability_metrics.energy_consumption', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="2500"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                Waste Reduction (%)
              </label>
              <input
                type="number"
                value={template.sustainability_metrics.waste_reduction}
                onChange={(e) => updateTemplate('sustainability_metrics.waste_reduction', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="15.2"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                Renewable Energy (%)
              </label>
              <input
                type="number"
                value={template.sustainability_metrics.renewable_energy_percentage}
                onChange={(e) => updateTemplate('sustainability_metrics.renewable_energy_percentage', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="85.0"
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <button
            onClick={resetTemplate}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>Reset</span>
          </button>
          
          <button
            onClick={downloadTemplate}
            disabled={!template.name.trim()}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download JSON</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default JSONTemplateGenerator;

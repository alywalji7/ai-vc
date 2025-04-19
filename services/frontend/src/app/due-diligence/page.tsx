'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface DueDiligenceResult {
  score: number;
  status: string;
  summary: string;
  findings: Array<{
    title: string;
    description: string;
    severity: string;
    evidence?: Record<string, any>;
    recommendations?: string[];
  }>;
  details: Record<string, any>;
  // Allow error property for modules that failed to run
  error?: string;
}

export default function DueDiligencePage() {
  const [companyId, setCompanyId] = useState('');
  const [modules, setModules] = useState<string[]>(['financial', 'tech']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, DueDiligenceResult> | null>(null);
  const [availableModules, setAvailableModules] = useState<string[]>([]);

  useEffect(() => {
    // Fetch available modules
    const fetchModules = async () => {
      try {
        const response = await fetch('/api/dd/modules');
        if (response.ok) {
          const data = await response.json();
          if (data.modules && Array.isArray(data.modules)) {
            setAvailableModules(data.modules);
            setModules(data.modules);
          }
        }
      } catch (error) {
        console.error('Error fetching modules:', error);
      }
    };

    fetchModules();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!companyId) {
      setError('Company ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await fetch('/api/dd/launch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_id: companyId, modules }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to launch due diligence');
      }

      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleModuleChange = (module: string) => {
    if (modules.includes(module)) {
      setModules(modules.filter(m => m !== module));
    } else {
      setModules([...modules, module]);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      case 'info':
      default:
        return 'text-blue-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pass':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'fail':
        return 'bg-red-100 text-red-800';
      case 'error':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Due Diligence Engine</h1>
        <p className="text-gray-600">
          Launch comprehensive due diligence checks on companies to evaluate their financial health, 
          technological capabilities, and potential risks.
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="companyId" className="block text-sm font-medium text-gray-700 mb-1">
              Company ID
            </label>
            <input
              type="text"
              id="companyId"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              placeholder="e.g., c003, c023"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Enter an ID for an existing company in the system.
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Due Diligence Modules
            </label>
            <div className="space-y-2">
              {availableModules.length > 0 ? (
                availableModules.map((module) => (
                  <div key={module} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`module-${module}`}
                      checked={modules.includes(module)}
                      onChange={() => handleModuleChange(module)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`module-${module}`} className="ml-2 block text-sm text-gray-900 capitalize">
                      {module} Due Diligence
                    </label>
                  </div>
                ))
              ) : (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="module-financial"
                    checked={modules.includes('financial')}
                    onChange={() => handleModuleChange('financial')}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="module-financial" className="ml-2 block text-sm text-gray-900 capitalize">
                    Financial Due Diligence
                  </label>
                </div>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
          >
            {loading ? 'Running Due Diligence...' : 'Launch Due Diligence'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-8 rounded">
          <p>{error}</p>
        </div>
      )}

      {results && Object.keys(results).length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Due Diligence Results</h2>
          
          <div className="space-y-8">
            {Object.entries(results).map(([moduleName, result]) => (
              <div key={moduleName} className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b">
                  <h3 className="text-lg font-semibold capitalize">{moduleName} Due Diligence</h3>
                </div>
                
                <div className="p-4">
                  {result.error ? (
                    <div className="text-red-600">{result.error}</div>
                  ) : (
                    <>
                      <div className="flex items-center mb-4">
                        <div className="mr-4">
                          <span className="block text-sm text-gray-500">Overall Score</span>
                          <span className={`text-2xl font-bold ${getScoreColor(result.score)}`}>
                            {(result.score * 100).toFixed(0)}%
                          </span>
                        </div>
                        
                        <div>
                          <span className="block text-sm text-gray-500">Status</span>
                          <span className={`inline-block px-2 py-1 text-sm font-semibold rounded ${getStatusColor(result.status)}`}>
                            {result.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mb-6">
                        <h4 className="text-sm font-medium text-gray-700 mb-1">Summary</h4>
                        <p className="text-gray-600">{result.summary}</p>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Key Findings</h4>
                        <div className="space-y-4">
                          {result.findings.map((finding, i) => (
                            <div key={i} className="border-l-4 pl-4" style={{ borderColor: finding.severity === 'critical' ? '#ef4444' : finding.severity === 'warning' ? '#f59e0b' : '#3b82f6' }}>
                              <h5 className={`font-semibold ${getSeverityColor(finding.severity)}`}>
                                {finding.title}
                              </h5>
                              <p className="text-sm text-gray-600 mt-1">{finding.description}</p>
                              
                              {finding.recommendations && finding.recommendations.length > 0 && (
                                <div className="mt-2">
                                  <h6 className="text-xs font-medium text-gray-500">Recommendations:</h6>
                                  <ul className="list-disc list-inside text-xs text-gray-600 ml-2">
                                    {finding.recommendations.map((rec, j) => (
                                      <li key={j}>{rec}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 text-center">
        <Link href="/" className="text-blue-600 hover:text-blue-800">
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
"use client";

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Head from 'next/head';

// Types
interface ImpactResult {
  changed_symbol: string;
  changed_symbol_type: string;
  changed_file: string;
  direct_callers: number;
  transitive_callers: number;
  affected_files: string[];
  affected_symbols: string[];
  risk_level: string;
  risk_score: number;
  confidence_score: number;
  call_chains: string[][];
  affected_nodes: any[];
  suggested_fix: string;
  ai_summary: string;
  analysis_depth: number;
  unresolved_symbols: string[];
}

interface RepositoryOverview {
  repository: string;
  total_files: number;
  language_breakdown: Record<string, number>;
  symbol_counts: {
    functions: number;
    classes: number;
    imports: number;
    exports: number;
  };
  call_graph_stats: any;
  import_graph_stats: any;
  critical_services: any[];
}

interface DiffAnalysisResult {
  success: boolean;
  results: ImpactResult[];
  summary: {
    total_changed_symbols: number;
    total_callers: number;
    total_files: number;
    overall_risk: string;
    average_confidence: number;
    changed_symbols: any[];
  };
  repository_stats: any;
}

interface PRCommentResult {
  success: boolean;
  comment: string;
}

// Risk level colors
const RISK_COLORS: Record<string, string> = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-yellow-500 text-black',
  low: 'bg-green-500 text-white',
};

const RISK_BADGE_COLORS: Record<string, string> = {
  critical: 'bg-red-600',
  high: 'bg-orange-600',
  medium: 'bg-yellow-500',
  low: 'bg-green-600',
};

export default function BlastRadiusPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'analyze' | 'diff' | 'visualize'>('overview');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [repositoryPath, setRepositoryPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Repository overview state
  const [repositoryOverview, setRepositoryOverview] = useState<RepositoryOverview | null>(null);
  
  // Single symbol analysis state
  const [symbolName, setSymbolName] = useState('');
  const [symbolType, setSymbolType] = useState('function');
  const [symbolFile, setSymbolFile] = useState('');
  const [impactResult, setImpactResult] = useState<ImpactResult | null>(null);
  
  // Diff analysis state
  const [diffInput, setDiffInput] = useState('');
  const [diffAnalysisResult, setDiffAnalysisResult] = useState<DiffAnalysisResult | null>(null);
  const [prComment, setPrComment] = useState('');
  
  // Available symbols for autocomplete
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  
  // Fetch repository overview
  const fetchRepositoryOverview = useCallback(async (path: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/blast-radius/repository-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repository_path: path }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRepositoryOverview(data);
      
      // Extract available symbols for autocomplete
      const symbols: string[] = [];
      if (data.repository_stats?.nodes) {
        Object.values(data.repository_stats.nodes).forEach((node: any) => {
          if (node.name) symbols.push(node.name);
        });
      }
      setAvailableSymbols(symbols);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch repository overview');
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // Analyze single symbol impact
  const analyzeSymbolImpact = useCallback(async () => {
    if (!repositoryPath || !symbolName) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/blast-radius/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryPath,
          symbol_name: symbolName,
          symbol_type: symbolType,
          file_path: symbolFile || undefined,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setImpactResult(data.result);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze impact');
    } finally {
      setIsLoading(false);
    }
  }, [repositoryPath, symbolName, symbolType, symbolFile]);
  
  // Analyze diff impact
  const analyzeDiffImpact = useCallback(async () => {
    if (!repositoryPath || !diffInput) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/blast-radius/analyze-diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryPath,
          diff: diffInput,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDiffAnalysisResult(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze diff');
    } finally {
      setIsLoading(false);
    }
  }, [repositoryPath, diffInput]);
  
  // Generate PR comment
  const generatePrComment = useCallback(async () => {
    if (!repositoryPath || !diffInput) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/blast-radius/generate-pr-comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryPath,
          diff: diffInput,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: PRCommentResult = await response.json();
      setPrComment(data.comment);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate PR comment');
    } finally {
      setIsLoading(false);
    }
  }, [repositoryPath, diffInput]);
  
  // Handle repository URL submission
  const handleRepositorySubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    // For now, we'll use a local path or assume the backend can handle GitHub URLs
    // In production, this would clone the repo first
    setRepositoryPath(repositoryUrl);
    await fetchRepositoryOverview(repositoryUrl);
    
  }, [repositoryUrl, fetchRepositoryOverview]);
  
  // Copy PR comment to clipboard
  const copyPrComment = useCallback(() => {
    if (!prComment) return;
    
    navigator.clipboard.writeText(prComment).then(() => {
      alert('PR comment copied to clipboard!');
    }).catch(() => {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = prComment;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert('PR comment copied to clipboard!');
    });
  }, [prComment]);
  
  // Format file count
  const formatNumber = (num: number) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
  };
  
  // Get risk badge class
  const getRiskBadgeClass = (riskLevel: string) => {
    return RISK_BADGE_COLORS[riskLevel.toLowerCase()] || 'bg-gray-500';
  };
  
  // Get risk color for graph nodes
  const getRiskColor = (riskLevel: string) => {
    const colors: Record<string, string> = {
      critical: '#ef4444',
      high: '#f97316',
      medium: '#eab308',
      low: '#22c55e',
    };
    return colors[riskLevel.toLowerCase()] || '#6b7280';
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Head>
        <title>Blast Radius - Impact Analysis</title>
        <meta name="description" content="Analyze the impact of code changes before you ship" />
      </Head>
      
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => router.push('/')} 
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-bold">Blast Radius</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Every code change has a blast radius. See it before production does.</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter repository URL or path..."
                  value={repositoryUrl}
                  onChange={(e) => setRepositoryUrl(e.target.value)}
                  className="bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-10 w-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && handleRepositorySubmit(e)}
                />
                <button 
                  onClick={handleRepositorySubmit}
                  disabled={isLoading}
                  className="absolute right-2 top-2 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
            <p>⚠️ {error}</p>
            <button onClick={() => setError(null)} className="mt-2 text-sm underline hover:no-underline">
              Dismiss
            </button>
          </div>
        )}
        
        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'overview' 
                  ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📊 Repository Overview
            </button>
            <button
              onClick={() => setActiveTab('analyze')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'analyze' 
                  ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              🎯 Analyze Symbol
            </button>
            <button
              onClick={() => setActiveTab('diff')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'diff' 
                  ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              🔥 Diff Analysis
            </button>
            <button
              onClick={() => setActiveTab('visualize')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'visualize' 
                  ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              🌐 Visualize Graph
            </button>
          </div>
        </div>
        
        {/* Tab Content */}
        <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Repository Overview</h2>
              
              {!repositoryOverview ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    Enter a repository URL above to get started
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Example: https://github.com/owner/repo or /path/to/local/repo
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Repository Info */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Repository</h3>
                    <p className="text-3xl font-bold">{repositoryOverview.repository}</p>
                    <p className="text-gray-500 dark:text-gray-400 mt-2">
                      {formatNumber(repositoryOverview.total_files)} files
                    </p>
                  </div>
                  
                  {/* Language Breakdown */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Languages</h3>
                    <div className="space-y-2">
                      {Object.entries(repositoryOverview.language_breakdown).map(([lang, count]) => (
                        <div key={lang} className="flex justify-between">
                          <span className="capitalize">{lang}</span>
                          <span className="font-medium">{count} files</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Symbol Counts */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Symbols</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Functions</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.symbol_counts.functions)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Classes</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.symbol_counts.classes)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Imports</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.symbol_counts.imports)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Exports</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.symbol_counts.exports)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Call Graph Stats */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Call Graph</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total Nodes</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.total_nodes || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Total Edges</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.total_edges || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Files</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.files || 0)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Import Graph Stats */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Import Graph</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total Nodes</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.total_nodes || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Total Edges</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.total_edges || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Languages</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.languages || 0)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Critical Services */}
                  <div className="md:col-span-2 lg:col-span-3 bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Critical Services</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                      Files with highest dependency fan-in (most critical)
                    </p>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-200 dark:border-gray-700">
                            <th className="text-left py-2 px-4 font-medium">File</th>
                            <th className="text-left py-2 px-4 font-medium">In-Degree</th>
                            <th className="text-left py-2 px-4 font-medium">Out-Degree</th>
                            <th className="text-left py-2 px-4 font-medium">Centrality</th>
                          </tr>
                        </thead>
                        <tbody>
                          {repositoryOverview.critical_services?.map((service, index) => (
                            <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                              <td className="py-2 px-4">{service.file}</td>
                              <td className="py-2 px-4">{service.in_degree}</td>
                              <td className="py-2 px-4">{service.out_degree}</td>
                              <td className="py-2 px-4">
                                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                  <div 
                                    className="bg-blue-600 h-2 rounded-full" 
                                    style={{ width: `${(service.centrality * 100).toFixed(0)}%` }}
                                  />
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'analyze' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Analyze Symbol Impact</h2>
              
              {!repositoryOverview ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    Please enter a repository URL first
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Symbol Name</label>
                      <input
                        type="text"
                        placeholder="e.g., processPayment"
                        value={symbolName}
                        onChange={(e) => setSymbolName(e.target.value)}
                        className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        list="symbols"
                      />
                      <datalist id="symbols">
                        {availableSymbols.map((symbol) => (
                          <option key={symbol} value={symbol} />
                        ))}
                      </datalist>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Symbol Type</label>
                      <select
                        value={symbolType}
                        onChange={(e) => setSymbolType(e.target.value)}
                        className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="function">Function</option>
                        <option value="class">Class</option>
                        <option value="method">Method</option>
                        <option value="variable">Variable</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">File Path (optional)</label>
                      <input
                        type="text"
                        placeholder="e.g., src/payments.py"
                        value={symbolFile}
                        onChange={(e) => setSymbolFile(e.target.value)}
                        className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  
                  <button
                    onClick={analyzeSymbolImpact}
                    disabled={isLoading || !symbolName}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
                  >
                    {isLoading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <span>Analyze Impact</span>
                      </>
                    )}
                  </button>
                  
                  {impactResult && (
                    <div className="mt-8 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                      {/* Hero Risk Card */}
                      <div className="mb-6">
                        <div className="flex items-center space-x-4 mb-4">
                          <h3 className="text-xl font-bold">Impact Analysis: {impactResult.changed_symbol}</h3>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBadgeClass(impactResult.risk_level)}`}>
                            {impactResult.risk_level.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                              {impactResult.direct_callers}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Direct Callers
                            </div>
                          </div>
                          
                          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                              {impactResult.transitive_callers}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Transitive Callers
                            </div>
                          </div>
                          
                          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                              {impactResult.affected_files.length}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Files Affected
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                          <div className="bg-white dark:bg-gray-900 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium">Risk Score</span>
                              <span className="text-lg font-bold">{impactResult.risk_score.toFixed(1)}</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${getRiskBadgeClass(impactResult.risk_level)}`}
                                style={{ width: `${Math.min(impactResult.risk_score * 5, 100)}%` }}
                              />
                            </div>
                          </div>
                          
                          <div className="bg-white dark:bg-gray-900 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium">Confidence</span>
                              <span className="text-lg font-bold">{Math.round(impactResult.confidence_score * 100)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${impactResult.confidence_score * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                        
                        {/* AI Summary */}
                        <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 mb-4">
                          <h4 className="font-medium mb-2">AI Summary</h4>
                          <p className="text-sm">{impactResult.ai_summary}</p>
                        </div>
                        
                        {/* Suggested Fix */}
                        <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4">
                          <h4 className="font-medium mb-2">Suggested Fix</h4>
                          <p className="text-sm">{impactResult.suggested_fix}</p>
                        </div>
                      </div>
                      
                      {/* Affected Files */}
                      <div className="mt-6">
                        <h4 className="font-medium mb-3">Affected Files</h4>
                        <div className="flex flex-wrap gap-2">
                          {impactResult.affected_files.slice(0, 10).map((file, index) => (
                            <span key={index} className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full text-sm">
                              {file}
                            </span>
                          ))}
                          {impactResult.affected_files.length > 10 && (
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              +{impactResult.affected_files.length - 10} more
                            </span>
                          )}
                        </div>
                      </div>
                      
                      {/* Affected Symbols */}
                      <div className="mt-6">
                        <h4 className="font-medium mb-3">Affected Symbols</h4>
                        <div className="flex flex-wrap gap-2">
                          {impactResult.affected_symbols.slice(0, 10).map((symbol, index) => (
                            <span key={index} className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full text-sm">
                              {symbol}
                            </span>
                          ))}
                          {impactResult.affected_symbols.length > 10 && (
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              +{impactResult.affected_symbols.length - 10} more
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'diff' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Diff Analysis</h2>
              
              {!repositoryOverview ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    Please enter a repository URL first
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Paste your git diff here
                    </label>
                    <textarea
                      placeholder="Paste git diff output here..."
                      value={diffInput}
                      onChange={(e) => setDiffInput(e.target.value)}
                      className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 h-64 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Example: git diff HEAD~1 HEAD
                    </p>
                  </div>
                  
                  <div className="flex space-x-4">
                    <button
                      onClick={analyzeDiffImpact}
                      disabled={isLoading || !diffInput}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
                    >
                      {isLoading ? (
                        <>
                          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          <span>Analyzing...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                          </svg>
                          <span>Analyze Diff</span>
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={generatePrComment}
                      disabled={isLoading || !diffInput}
                      className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span>Generate PR Comment</span>
                    </button>
                  </div>
                  
                  {diffAnalysisResult && (
                    <div className="mt-8">
                      {/* Summary Card */}
                      <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-xl font-bold">Diff Analysis Summary</h3>
                          <span className={`px-4 py-2 rounded-lg font-medium ${
                            RISK_COLORS[diffAnalysisResult.summary.overall_risk.toLowerCase()] || 'bg-gray-500 text-white'
                          }`}>
                            {diffAnalysisResult.summary.overall_risk.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                          <div className="text-center">
                            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                              {diffAnalysisResult.summary.total_changed_symbols}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Symbols Changed
                            </div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                              {diffAnalysisResult.summary.total_callers}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Total Callers
                            </div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                              {diffAnalysisResult.summary.total_files}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Files Impacted
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white dark:bg-gray-900 rounded-lg p-4 mb-4">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Average Confidence</span>
                            <span className="text-lg font-bold">
                              {Math.round(diffAnalysisResult.summary.average_confidence * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ 
                                width: `${diffAnalysisResult.summary.average_confidence * 100}%` 
                              }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {/* Individual Results */}
                      <div className="space-y-4">
                        {diffAnalysisResult.results.map((result, index) => (
                          <div key={index} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-medium">
                                {index + 1}. {result.changed_symbol} ({result.changed_symbol_type})
                              </h4>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                getRiskBadgeClass(result.risk_level)
                              }`}>
                                {result.risk_level.toUpperCase()}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                              <div className="text-center">
                                <div className="font-bold">{result.direct_callers}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Direct</div>
                              </div>
                              <div className="text-center">
                                <div className="font-bold">{result.transitive_callers}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Transitive</div>
                              </div>
                              <div className="text-center">
                                <div className="font-bold">{result.affected_files.length}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Files</div>
                              </div>
                              <div className="text-center">
                                <div className="font-bold">{result.risk_score.toFixed(1)}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Risk Score</div>
                              </div>
                            </div>
                            
                            <div className="text-sm text-gray-600 dark:text-gray-300">
                              {result.ai_summary}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {prComment && (
                    <div className="mt-8 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold">PR Review Comment</h3>
                        <button
                          onClick={copyPrComment}
                          className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 px-3 py-1 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span>Copy</span>
                        </button>
                      </div>
                      
                      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto whitespace-pre-wrap">
                        {prComment}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'visualize' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Blast Radius Visualization</h2>
              
              {!repositoryOverview ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    Please enter a repository URL first
                  </p>
                </div>
              ) : !impactResult && !diffAnalysisResult ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    Run an analysis first (Analyze Symbol or Diff Analysis)
                  </p>
                </div>
              ) : (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {impactResult ? 
                      `Impact Visualization: ${impactResult.changed_symbol}` : 
                      'Diff Impact Visualization'
                    }
                  </h3>
                  
                  <div className="bg-white dark:bg-gray-900 rounded-lg p-8 min-h-96 flex items-center justify-center">
                    <div className="text-center">
                      <div className="mb-4">
                        <svg className="w-24 h-24 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <p className="text-gray-500 dark:text-gray-400 mb-4">
                        Interactive graph visualization coming soon!
                      </p>
                      <p className="text-sm text-gray-400 dark:text-gray-500">
                        The blast radius graph will show nodes pulsing outward from the changed symbol,
                        color-coded by risk level (red = critical, orange = high, yellow = medium, green = low).
                      </p>
                      
                      {/* Show text representation for now */}
                      <div className="mt-8 text-left">
                        <h4 className="font-medium mb-4">Text Representation:</h4>
                        
                        {impactResult && (
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <span className="w-3 h-3 rounded-full bg-red-500"></span>
                              <span>{impactResult.changed_symbol} (changed)</span>
                            </div>
                            
                            {impactResult.affected_nodes.slice(0, 5).map((node, index) => (
                              <div key={index} className="flex items-center space-x-2 ml-4">
                                <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                                <span className="text-sm">{node.name} ({node.file_path})</span>
                              </div>
                            ))}
                            
                            {impactResult.affected_nodes.length > 5 && (
                              <div className="ml-4 text-sm text-gray-500 dark:text-gray-400">
                                +{impactResult.affected_nodes.length - 5} more affected nodes
                              </div>
                            )}
                          </div>
                        )}
                        
                        {diffAnalysisResult && !impactResult && (
                          <div className="space-y-4">
                            {diffAnalysisResult.results.map((result, resultIndex) => (
                              <div key={resultIndex} className="space-y-2">
                                <div className="flex items-center space-x-2">
                                  <span className="w-3 h-3 rounded-full bg-red-500"></span>
                                  <span>{result.changed_symbol} (changed)</span>
                                </div>
                                
                                {result.affected_nodes.slice(0, 3).map((node: any, nodeIndex: number) => (
                                  <div key={nodeIndex} className="flex items-center space-x-2 ml-4">
                                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                                    <span className="text-sm">{node.name} ({node.file_path})</span>
                                  </div>
                                ))}
                                
                                {result.affected_nodes.length > 3 && (
                                  <div className="ml-4 text-sm text-gray-500 dark:text-gray-400">
                                    +{result.affected_nodes.length - 3} more affected nodes
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Built for the OpenAI Codex Hackathon × NamasteDev
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Every code change has a blast radius. See it before production does.
          </p>
        </div>
      </footer>
    </div>
  );
}

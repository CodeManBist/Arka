"use client";

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Head from 'next/head';
import GraphVisualization from '@/components/GraphVisualization';

// Types
type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

type ImpactResult = {
  changed_symbol: string;
  changed_symbol_type: string;
  changed_file: string;
  direct_callers: number;
  transitive_callers: number;
  affected_files: string[];
  affected_symbols: string[];
  risk_level: RiskLevel;
  risk_score: number;
  confidence_score: number;
  call_chains: string[][];
  affected_nodes: any[];
  suggested_fix: string;
  ai_summary: string;
  analysis_depth: number;
  unresolved_symbols: string[];
};

type RepositoryOverview = {
  repository: string;
  repository_path: string;
  is_temporary: boolean;
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
};

type DiffAnalysisResult = {
  success: boolean;
  results: ImpactResult[];
  summary: {
    total_changed_symbols: number;
    total_callers: number;
    total_files: number;
    overall_risk: RiskLevel;
    average_confidence: number;
    changed_symbols: any[];
  };
  repository_stats: any;
};

type PRCommentResult = {
  success: boolean;
  comment: string;
};

// Constants
const API_BASE_URL = 'http://localhost:8000';

const RISK_COLORS: Record<RiskLevel, { bg: string; text: string; border: string }> = {
  critical: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-500' },
  high: { bg: 'bg-orange-600', text: 'text-white', border: 'border-orange-500' },
  medium: { bg: 'bg-yellow-500', text: 'text-black', border: 'border-yellow-500' },
  low: { bg: 'bg-green-600', text: 'text-white', border: 'border-green-500' },
};

const RISK_BADGE_COLORS: Record<RiskLevel, string> = {
  critical: 'bg-red-600',
  high: 'bg-orange-600',
  medium: 'bg-yellow-500',
  low: 'bg-green-600',
};

const RISK_EMOJIS: Record<RiskLevel, string> = {
  critical: '🔴',
  high: '🟠',
  medium: '🟡',
  low: '🟢',
};

const RISK_LABELS: Record<RiskLevel, string> = {
  critical: 'CRITICAL',
  high: 'HIGH',
  medium: 'MEDIUM',
  low: 'LOW',
};

// Skeleton Loader Component
const SkeletonLoader = ({ className = '' }: { className?: string }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg ${className}`} />
);

// Loading Spinner Component
const LoadingSpinner = ({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };
  
  return (
    <svg 
      className={`animate-spin ${sizeClasses[size]} text-blue-600 dark:text-blue-400`} 
      xmlns="http://www.w3.org/2000/svg" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path 
        className="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// Error Alert Component
const ErrorAlert = ({ 
  message, 
  onDismiss 
}: { 
  message: string; 
  onDismiss: () => void 
}) => (
  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-xl flex items-start justify-between">
    <div className="flex items-start space-x-3">
      <span className="text-red-500 dark:text-red-400 mt-0.5">⚠️</span>
      <p className="text-red-700 dark:text-red-300">{message}</p>
    </div>
    <button 
      onClick={onDismiss}
      className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors p-1 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
);

// Success Alert Component
const SuccessAlert = ({ 
  message, 
  onDismiss 
}: { 
  message: string; 
  onDismiss: () => void 
}) => (
  <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-300 dark:border-green-700 rounded-xl flex items-start justify-between">
    <div className="flex items-start space-x-3">
      <span className="text-green-500 dark:text-green-400 mt-0.5">✅</span>
      <p className="text-green-700 dark:text-green-300">{message}</p>
    </div>
    <button 
      onClick={onDismiss}
      className="text-green-500 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 transition-colors p-1 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/50"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
);

// Risk Badge Component
const RiskBadge = ({ riskLevel }: { riskLevel: RiskLevel }) => (
  <span className={`px-3 py-1 rounded-full text-sm font-medium ${RISK_BADGE_COLORS[riskLevel]} text-white`}>
    {RISK_EMOJIS[riskLevel]} {RISK_LABELS[riskLevel]}
  </span>
);

// Stat Card Component
const StatCard = ({ 
  label, 
  value, 
  icon, 
  color = 'blue',
  loading = false 
}: { 
  label: string; 
  value: string | number; 
  icon: React.ReactNode; 
  color?: string; 
  loading?: boolean 
}) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    orange: 'bg-orange-500',
    yellow: 'bg-yellow-500',
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          {icon}
        </div>
        {loading ? (
          <LoadingSpinner size="sm" />
        ) : (
          <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">{value}</span>
        )}
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
    </div>
  );
};

// Progress Bar Component
const ProgressBar = ({ 
  value, 
  max = 100,
  color = 'blue',
  className = ''
}: { 
  value: number; 
  max?: number; 
  color?: string; 
  className?: string 
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const colorClasses = {
    blue: 'bg-blue-600',
    red: 'bg-red-600',
    orange: 'bg-orange-600',
    yellow: 'bg-yellow-500',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
  };
  
  return (
    <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 ${className}`}>
      <div 
        className={`h-2 rounded-full ${colorClasses[color]} transition-all duration-300`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

// Repository Card Component
const RepositoryCard = ({ 
  repository, 
  loading = false 
}: { 
  repository: RepositoryOverview | null; 
  loading?: boolean 
}) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
        <SkeletonLoader className="h-8 w-1/2 mb-4" />
        <SkeletonLoader className="h-4 w-1/3 mb-2" />
        <SkeletonLoader className="h-4 w-1/4" />
      </div>
    );
  }
  
  if (!repository) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-100 dark:border-gray-700 text-center">
        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
          <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <p className="text-gray-500 dark:text-gray-400 mb-2">
          Enter a repository URL above to get started
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          Example: https://github.com/owner/repo or /path/to/local/repo
        </p>
      </div>
    );
  }
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{repository.repository}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {repository.is_temporary ? 'Cloned temporarily' : 'Local repository'}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm text-green-600 dark:text-green-400 font-medium">Connected</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {repository.total_files.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Files</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {repository.symbol_counts.functions.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Functions</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {repository.symbol_counts.classes.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Classes</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {Object.keys(repository.language_breakdown).length}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Languages</div>
        </div>
      </div>
      
      <div className="border-t border-gray-100 dark:border-gray-700 pt-4">
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Languages</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(repository.language_breakdown).map(([lang, count]) => (
            <span 
              key={lang} 
              className="bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full text-sm text-gray-600 dark:text-gray-300"
            >
              {lang}: {count}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Impact Result Card Component
const ImpactResultCard = ({ 
  result, 
  loading = false 
}: { 
  result: ImpactResult | null; 
  loading?: boolean 
}) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
        <SkeletonLoader className="h-6 w-1/2 mb-4" />
        <div className="grid grid-cols-3 gap-4 mb-4">
          <SkeletonLoader className="h-20" />
          <SkeletonLoader className="h-20" />
          <SkeletonLoader className="h-20" />
        </div>
        <SkeletonLoader className="h-4 w-full mb-2" />
        <SkeletonLoader className="h-4 w-3/4" />
      </div>
    );
  }
  
  if (!result) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-100 dark:border-gray-700 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          Run an analysis to see results
        </p>
      </div>
    );
  }
  
  const riskLevel = result.risk_level as RiskLevel;
  const riskColor = RISK_COLORS[riskLevel];
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Impact Analysis: {result.changed_symbol}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {result.changed_symbol_type} in {result.changed_file}
          </p>
        </div>
        <RiskBadge riskLevel={riskLevel} />
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatCard
          label="Direct Callers"
          value={result.direct_callers}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>}
          color="blue"
        />
        <StatCard
          label="Transitive Callers"
          value={result.transitive_callers}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>}
          color="purple"
        />
        <StatCard
          label="Files Affected"
          value={result.affected_files.length}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>}
          color="green"
        />
      </div>
      
      {/* Risk and Confidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Risk Score</span>
            <span className="text-lg font-bold text-gray-900 dark:text-gray-100">{result.risk_score.toFixed(1)}</span>
          </div>
          <ProgressBar 
            value={Math.min(result.risk_score * 5, 100)} 
            color={riskLevel}
          />
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Confidence</span>
            <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {Math.round(result.confidence_score * 100)}%
            </span>
          </div>
          <ProgressBar 
            value={result.confidence_score * 100} 
            color="blue"
          />
        </div>
      </div>
      
      {/* AI Summary and Suggested Fix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4">
          <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">AI Summary</h4>
          <p className="text-sm text-blue-800 dark:text-blue-200">{result.ai_summary}</p>
        </div>
        <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4">
          <h4 className="font-medium text-green-700 dark:text-green-300 mb-2">Suggested Fix</h4>
          <p className="text-sm text-green-800 dark:text-green-200">{result.suggested_fix}</p>
        </div>
      </div>
      
      {/* Affected Files */}
      {result.affected_files.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Affected Files</h4>
          <div className="flex flex-wrap gap-2">
            {result.affected_files.slice(0, 10).map((file, index) => (
              <span 
                key={index} 
                className="bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full text-sm text-gray-600 dark:text-gray-300"
              >
                {file}
              </span>
            ))}
            {result.affected_files.length > 10 && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                +{result.affected_files.length - 10} more
              </span>
            )}
          </div>
        </div>
      )}
      
      {/* Affected Symbols */}
      {result.affected_symbols.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Affected Symbols</h4>
          <div className="flex flex-wrap gap-2">
            {result.affected_symbols.slice(0, 10).map((symbol, index) => (
              <span 
                key={index} 
                className="bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full text-sm text-gray-600 dark:text-gray-300"
              >
                {symbol}
              </span>
            ))}
            {result.affected_symbols.length > 10 && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                +{result.affected_symbols.length - 10} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Diff Analysis Summary Component
const DiffAnalysisSummary = ({ 
  result, 
  loading = false 
}: { 
  result: DiffAnalysisResult | null; 
  loading?: boolean 
}) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
        <SkeletonLoader className="h-6 w-1/2 mb-4" />
        <div className="grid grid-cols-3 gap-4 mb-4">
          <SkeletonLoader className="h-20" />
          <SkeletonLoader className="h-20" />
          <SkeletonLoader className="h-20" />
        </div>
      </div>
    );
  }
  
  if (!result || !result.success) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-100 dark:border-gray-700 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          {result?.results?.length === 0 ? 'No changed symbols detected in the diff' : 'Run a diff analysis to see results'}
        </p>
      </div>
    );
  }
  
  const summary = result.summary;
  const overallRisk = summary.overall_risk as RiskLevel;
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">Diff Analysis Summary</h3>
        <RiskBadge riskLevel={overallRisk} />
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatCard
          label="Symbols Changed"
          value={summary.total_changed_symbols}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>}
          color="blue"
        />
        <StatCard
          label="Total Callers"
          value={summary.total_callers}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>}
          color="purple"
        />
        <StatCard
          label="Files Impacted"
          value={summary.total_files}
          icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>}
          color="green"
        />
      </div>
      
      {/* Average Confidence */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Average Confidence</span>
          <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
            {Math.round(summary.average_confidence * 100)}%
          </span>
        </div>
        <ProgressBar 
          value={summary.average_confidence * 100} 
          color="blue"
        />
      </div>
      
      {/* Changed Symbols */}
      {summary.changed_symbols && summary.changed_symbols.length > 0 && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Changed Symbols</h4>
          <div className="space-y-2">
            {summary.changed_symbols.slice(0, 5).map((symbol: any, index) => {
              const changeTypeEmoji = {
                added: '✅',
                modified: '🔵',
                deleted: '❌',
              };
              const emoji = changeTypeEmoji[symbol.change_type as keyof typeof changeTypeEmoji] || '📝';
              
              return (
                <div 
                  key={index} 
                  className="flex items-center space-x-3 bg-gray-50 dark:bg-gray-900 rounded-lg p-3"
                >
                  <span className="text-lg">{emoji}</span>
                  <div className="flex-1">
                    <code className="font-medium text-gray-900 dark:text-gray-100">
                      {symbol.name}
                    </code>
                    <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                      ({symbol.type}) in {symbol.file}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// Individual Diff Result Component
const IndividualDiffResult = ({ 
  result, 
  index 
}: { 
  result: ImpactResult; 
  index: number 
}) => {
  const riskLevel = result.risk_level as RiskLevel;
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-gray-900 dark:text-gray-100">
          {index + 1}. {result.changed_symbol} ({result.changed_symbol_type})
        </h4>
        <RiskBadge riskLevel={riskLevel} />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
        <div className="text-center">
          <div className="font-bold text-gray-900 dark:text-gray-100">{result.direct_callers}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Direct</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-gray-900 dark:text-gray-100">{result.transitive_callers}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Transitive</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-gray-900 dark:text-gray-100">{result.affected_files.length}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Files</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-gray-900 dark:text-gray-100">{result.risk_score.toFixed(1)}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Risk Score</div>
        </div>
      </div>
      
      <div className="text-sm text-gray-600 dark:text-gray-300">
        {result.ai_summary}
      </div>
    </div>
  );
};

// PR Comment Component
const PRComment = ({ 
  comment, 
  loading = false,
  onCopy 
}: { 
  comment: string; 
  loading?: boolean; 
  onCopy: () => void 
}) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
        <SkeletonLoader className="h-6 w-1/2 mb-4" />
        <SkeletonLoader className="h-4 w-full mb-2" />
        <SkeletonLoader className="h-4 w-3/4 mb-2" />
        <SkeletonLoader className="h-4 w-1/2" />
      </div>
    );
  }
  
  if (!comment) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-100 dark:border-gray-700 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          Generate a PR comment to see it here
        </p>
      </div>
    );
  }
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">PR Review Comment</h3>
        <button
          onClick={onCopy}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span>Copy to Clipboard</span>
        </button>
      </div>
      
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto whitespace-pre-wrap">
        {comment}
      </div>
      
      <div className="mt-4 text-center">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Ready to paste into GitHub PR review
        </span>
      </div>
    </div>
  );
};

// Main Component
export default function BlastRadiusPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'analyze' | 'diff' | 'visualize'>('overview');
  const [repositoryInput, setRepositoryInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Repository overview state
  const [repositoryOverview, setRepositoryOverview] = useState<RepositoryOverview | null>(null);
  
  // Single symbol analysis state
  const [symbolName, setSymbolName] = useState('');
  const [symbolType, setSymbolType] = useState<'function' | 'class' | 'method' | 'variable'>('function');
  const [symbolFile, setSymbolFile] = useState('');
  const [impactResult, setImpactResult] = useState<ImpactResult | null>(null);
  const [analyzingSymbol, setAnalyzingSymbol] = useState(false);
  
  // Diff analysis state
  const [diffInput, setDiffInput] = useState('');
  const [diffAnalysisResult, setDiffAnalysisResult] = useState<DiffAnalysisResult | null>(null);
  const [analyzingDiff, setAnalyzingDiff] = useState(false);
  const [prComment, setPrComment] = useState('');
  const [generatingComment, setGeneratingComment] = useState(false);
  
  // Available symbols for autocomplete
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  
  // Format number
  const formatNumber = (num: number) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
  };
  
  // Dismiss error
  const dismissError = useCallback(() => {
    setError(null);
  }, []);
  
  // Dismiss success
  const dismissSuccess = useCallback(() => {
    setSuccess(null);
  }, []);
  
  // Fetch repository overview
  const fetchRepositoryOverview = useCallback(async (input: string) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/blast-radius/repository-overview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repository_path: input }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || errorData.detail || `HTTP error! status: ${response.status}`
        );
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch repository overview');
      }
      
      setRepositoryOverview(data);
      setSuccess(`Successfully loaded repository: ${data.repository}`);
      
      // Extract available symbols for autocomplete
      const symbols: string[] = [];
      if (data.call_graph_stats?.nodes) {
        // This would need to be adjusted based on actual response structure
        // For now, we'll use a simple approach
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
    if (!repositoryOverview || !symbolName) {
      setError('Please enter a repository and symbol name');
      return;
    }
    
    setAnalyzingSymbol(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/blast-radius/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryOverview.repository_path || repositoryOverview.repository,
          symbol_name: symbolName,
          symbol_type: symbolType,
          file_path: symbolFile || undefined,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || errorData.detail || `HTTP error! status: ${response.status}`
        );
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to analyze impact');
      }
      
      setImpactResult(data.result);
      setSuccess(`Successfully analyzed impact for: ${symbolName}`);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze impact');
    } finally {
      setAnalyzingSymbol(false);
    }
  }, [repositoryOverview, symbolName, symbolType, symbolFile]);
  
  // Analyze diff impact
  const analyzeDiffImpact = useCallback(async () => {
    if (!repositoryOverview || !diffInput) {
      setError('Please enter a repository and paste a diff');
      return;
    }
    
    setAnalyzingDiff(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/blast-radius/analyze-diff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryOverview.repository_path || repositoryOverview.repository,
          diff: diffInput,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || errorData.detail || `HTTP error! status: ${response.status}`
        );
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to analyze diff');
      }
      
      setDiffAnalysisResult(data);
      setSuccess(`Successfully analyzed diff with ${data.summary?.total_changed_symbols || 0} changed symbols`);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze diff');
    } finally {
      setAnalyzingDiff(false);
    }
  }, [repositoryOverview, diffInput]);
  
  // Generate PR comment
  const generatePrComment = useCallback(async () => {
    if (!repositoryOverview || !diffInput) {
      setError('Please enter a repository and paste a diff');
      return;
    }
    
    setGeneratingComment(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/blast-radius/generate-pr-comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryOverview.repository_path || repositoryOverview.repository,
          diff: diffInput,
          max_depth: 3,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || errorData.detail || `HTTP error! status: ${response.status}`
        );
      }
      
      const data: PRCommentResult = await response.json();
      
      if (!data.success) {
        throw new Error(data.comment || 'Failed to generate PR comment');
      }
      
      setPrComment(data.comment);
      setSuccess('PR comment generated successfully!');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate PR comment');
    } finally {
      setGeneratingComment(false);
    }
  }, [repositoryOverview, diffInput]);
  
  // Copy PR comment to clipboard
  const copyPrComment = useCallback(() => {
    if (!prComment) return;
    
    navigator.clipboard.writeText(prComment).then(() => {
      setSuccess('PR comment copied to clipboard!');
    }).catch(() => {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = prComment;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setSuccess('PR comment copied to clipboard!');
    });
  }, [prComment]);
  
  // Handle repository input submission
  const handleRepositorySubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    if (!repositoryInput.trim()) {
      setError('Please enter a repository URL or path');
      return;
    }
    
    await fetchRepositoryOverview(repositoryInput);
  }, [repositoryInput, fetchRepositoryOverview]);
  
  // Tab change handler
  const handleTabChange = useCallback((tab: 'overview' | 'analyze' | 'diff' | 'visualize') => {
    setActiveTab(tab);
    setError(null);
    setSuccess(null);
  }, []);
  
  // Clear all state
  const clearAll = useCallback(() => {
    setRepositoryInput('');
    setRepositoryOverview(null);
    setSymbolName('');
    setSymbolType('function');
    setSymbolFile('');
    setImpactResult(null);
    setDiffInput('');
    setDiffAnalysisResult(null);
    setPrComment('');
    setError(null);
    setSuccess(null);
  }, []);
  
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
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
              >
                <svg className="w-6 h-6 text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-bold">Blast Radius</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Every code change has a blast radius. See it before production does.
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={clearAll}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Clear All</span>
              </button>
              
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter repository URL or path..."
                  value={repositoryInput}
                  onChange={(e) => setRepositoryInput(e.target.value)}
                  className="bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-10 w-80 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  onKeyPress={(e) => e.key === 'Enter' && handleRepositorySubmit()}
                  disabled={isLoading}
                />
                <button 
                  onClick={handleRepositorySubmit}
                  disabled={isLoading || !repositoryInput.trim()}
                  className="absolute right-2 top-2 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  {isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <svg className="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error and Success Alerts */}
        {error && <ErrorAlert message={error} onDismiss={dismissError} />}
        {success && <SuccessAlert message={success} onDismiss={dismissSuccess} />}
        
        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
            {[
              { id: 'overview', label: '📊 Repository Overview', icon: '📊' },
              { id: 'analyze', label: '💥 Analyze Symbol', icon: '💥' },
              { id: 'diff', label: '📝 Diff Analysis', icon: '📝' },
              { id: 'visualize', label: '🌐 Visualize Graph', icon: '🌐' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id 
                    ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-lg' 
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
        
        {/* Tab Content */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
          {activeTab === 'overview' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Repository Overview</h2>
              
              <RepositoryCard 
                repository={repositoryOverview} 
                loading={isLoading}
              />
              
              {/* Additional Stats */}
              {repositoryOverview && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Call Graph</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Total Nodes</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.total_nodes || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Total Edges</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.total_edges || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Files</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.call_graph_stats?.files || 0)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Import Graph</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Total Nodes</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.total_nodes || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Total Edges</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.total_edges || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Languages</span>
                        <span className="font-medium">{formatNumber(repositoryOverview.import_graph_stats?.languages || 0)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Critical Services */}
              {repositoryOverview?.critical_services?.length > 0 && (
                <div className="mt-6 bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4">Critical Services</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    Files with highest dependency fan-in (most critical)
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200 dark:border-gray-700">
                          <th className="text-left py-2 px-4 font-medium text-gray-500 dark:text-gray-400">File</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-500 dark:text-gray-400">In-Degree</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-500 dark:text-gray-400">Out-Degree</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-500 dark:text-gray-400">Centrality</th>
                        </tr>
                      </thead>
                      <tbody>
                        {repositoryOverview.critical_services.map((service, index) => (
                          <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                            <td className="py-2 px-4 text-gray-900 dark:text-gray-100">{service.file}</td>
                            <td className="py-2 px-4 text-gray-900 dark:text-gray-100">{service.in_degree}</td>
                            <td className="py-2 px-4 text-gray-900 dark:text-gray-100">{service.out_degree}</td>
                            <td className="py-2 px-4">
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
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
              )}
            </div>
          )}
          
          {activeTab === 'analyze' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Analyze Symbol Impact</h2>
              
              {!repositoryOverview ? (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-12 text-center">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 mb-2">
                    Please enter a repository URL above to get started
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Example: https://github.com/owner/repo or /path/to/local/repo
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Symbol Information</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Symbol Name
                        </label>
                        <input
                          type="text"
                          placeholder="e.g., processPayment"
                          value={symbolName}
                          onChange={(e) => setSymbolName(e.target.value)}
                          className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                          list="symbols"
                        />
                        <datalist id="symbols">
                          {availableSymbols.map((symbol) => (
                            <option key={symbol} value={symbol} />
                          ))}
                        </datalist>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Symbol Type
                        </label>
                        <select
                          value={symbolType}
                          onChange={(e) => setSymbolType(e.target.value as any)}
                          className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        >
                          <option value="function">Function</option>
                          <option value="class">Class</option>
                          <option value="method">Method</option>
                          <option value="variable">Variable</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          File Path (optional)
                        </label>
                        <input
                          type="text"
                          placeholder="e.g., src/payments.py"
                          value={symbolFile}
                          onChange={(e) => setSymbolFile(e.target.value)}
                          className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                      </div>
                    </div>
                    
                    <button
                      onClick={analyzeSymbolImpact}
                      disabled={analyzingSymbol || !symbolName}
                      className="mt-6 w-full md:w-auto bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl disabled:shadow-none"
                    >
                      {analyzingSymbol ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span>Analyzing Impact...</span>
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
                  </div>
                  
                  <ImpactResultCard 
                    result={impactResult} 
                    loading={analyzingSymbol}
                  />
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'diff' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Diff Analysis</h2>
              
              {!repositoryOverview ? (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-12 text-center">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 mb-2">
                    Please enter a repository URL above to get started
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Example: https://github.com/owner/repo or /path/to/local/repo
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Git Diff</h3>
                    
                    <textarea
                      placeholder="Paste your git diff here..."
                      value={diffInput}
                      onChange={(e) => setDiffInput(e.target.value)}
                      className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 h-64 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Example: git diff HEAD~1 HEAD or paste diff from GitHub PR
                    </p>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-4">
                    <button
                      onClick={analyzeDiffImpact}
                      disabled={analyzingDiff || !diffInput}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl disabled:shadow-none"
                    >
                      {analyzingDiff ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span>Analyzing Diff...</span>
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
                      disabled={generatingComment || !diffInput}
                      className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl disabled:shadow-none"
                    >
                      {generatingComment ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span>Generating Comment...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span>Generate PR Comment</span>
                        </>
                      )}
                    </button>
                  </div>
                  
                  {/* Diff Analysis Results */}
                  <DiffAnalysisSummary 
                    result={diffAnalysisResult} 
                    loading={analyzingDiff}
                  />
                  
                  {/* Individual Results */}
                  {diffAnalysisResult?.results?.length > 0 && (
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                        Individual Impact Analyses
                      </h3>
                      {diffAnalysisResult.results.map((result, index) => (
                        <IndividualDiffResult 
                          key={index} 
                          result={result} 
                          index={index}
                        />
                      ))}
                    </div>
                  )}
                  
                  {/* PR Comment */}
                  <PRComment 
                    comment={prComment}
                    loading={generatingComment}
                    onCopy={copyPrComment}
                  />
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'visualize' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Blast Radius Visualization</h2>
              
              <GraphVisualization
                data={{
                  nodes: impactResult ? [
                    {
                      id: impactResult.changed_symbol,
                      name: impactResult.changed_symbol,
                      type: impactResult.changed_symbol_type,
                      file_path: impactResult.changed_file,
                      risk_level: impactResult.risk_level as RiskLevel,
                      is_changed: true,
                      depth: 0
                    },
                    ...(impactResult.affected_nodes || []).slice(0, 50).map((node: any, i: number) => ({
                      id: node.id || `${node.name}_${i}`,
                      name: node.name,
                      type: node.type,
                      file_path: node.file_path,
                      risk_level: node.risk_level as RiskLevel || 'medium',
                      is_changed: false,
                      depth: i < 10 ? 1 : i < 20 ? 2 : 3
                    }))
                  ] : diffAnalysisResult?.results?.flatMap((result, resultIndex) => [
                    {
                      id: result.changed_symbol,
                      name: result.changed_symbol,
                      type: result.changed_symbol_type,
                      file_path: result.changed_file,
                      risk_level: result.risk_level as RiskLevel,
                      is_changed: true,
                      depth: 0
                    },
                    ...(result.affected_nodes || []).slice(0, 20).map((node: any, i: number) => ({
                      id: node.id || `${node.name}_${resultIndex}_${i}`,
                      name: node.name,
                      type: node.type,
                      file_path: node.file_path,
                      risk_level: node.risk_level as RiskLevel || 'medium',
                      is_changed: false,
                      depth: i < 5 ? 1 : i < 10 ? 2 : 3
                    }))
                  ]) || [],
                  edges: impactResult ? [
                    ...(impactResult.call_chains || []).slice(0, 30).map((chain, i) => ({
                      source: chain[0] || impactResult.changed_symbol,
                      target: chain[chain.length - 1] || impactResult.changed_symbol,
                      type: 'call'
                    }))
                  ] : diffAnalysisResult?.results?.flatMap(result =>
                    (result.call_chains || []).slice(0, 10).map((chain, i) => ({
                      source: chain[0] || result.changed_symbol,
                      target: chain[chain.length - 1] || result.changed_symbol,
                      type: 'call'
                    }))
                  ) || []
                }}
                changedSymbol={impactResult?.changed_symbol || diffAnalysisResult?.results?.[0]?.changed_symbol}
                loading={analyzingSymbol || analyzingDiff}
              />
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

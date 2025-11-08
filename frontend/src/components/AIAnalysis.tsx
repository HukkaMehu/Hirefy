import React from 'react';
import { Brain, AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react';

interface AIAnalysisProps {
  analysis: {
    verification_assessment?: string;
    risk_analysis?: string;
    cross_reference_validation?: string;
    fraud_detection?: string;
    technical_competency?: string;
    recommendations?: string;
    follow_up_actions?: string;
    summary?: string;
  };
}

export function AIAnalysis({ analysis }: AIAnalysisProps) {
  if (!analysis) {
    return null;
  }

  const sections = [
    {
      key: 'verification_assessment',
      title: 'Overall Assessment',
      icon: CheckCircle,
      color: 'text-blue-600'
    },
    {
      key: 'risk_analysis',
      title: 'Risk Analysis',
      icon: AlertTriangle,
      color: 'text-yellow-600'
    },
    {
      key: 'fraud_detection',
      title: 'Fraud Detection',
      icon: XCircle,
      color: 'text-red-600'
    },
    {
      key: 'cross_reference_validation',
      title: 'Cross-Reference Validation',
      icon: CheckCircle,
      color: 'text-green-600'
    },
    {
      key: 'technical_competency',
      title: 'Technical Competency',
      icon: TrendingUp,
      color: 'text-purple-600'
    },
    {
      key: 'recommendations',
      title: 'Recommendations',
      icon: Brain,
      color: 'text-indigo-600'
    },
    {
      key: 'follow_up_actions',
      title: 'Follow-up Actions',
      icon: CheckCircle,
      color: 'text-teal-600'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="flex items-center gap-3 border-b pb-4">
        <Brain className="w-8 h-8 text-indigo-600" />
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Analysis</h2>
          <p className="text-sm text-gray-600">Comprehensive verification assessment powered by AI</p>
        </div>
      </div>

      {analysis.summary && (
        <div className="bg-indigo-50 border-l-4 border-indigo-600 p-4 rounded">
          <h3 className="font-semibold text-indigo-900 mb-2">Executive Summary</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{analysis.summary}</p>
        </div>
      )}

      <div className="space-y-4">
        {sections.map(section => {
          const content = analysis[section.key as keyof typeof analysis];
          if (!content) return null;

          const Icon = section.icon;

          return (
            <div key={section.key} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3">
                <Icon className={`w-5 h-5 mt-1 ${section.color} flex-shrink-0`} />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">{section.title}</h3>
                  <div className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                    {content}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t text-xs text-gray-500 flex items-center gap-2">
        <Brain className="w-4 h-4" />
        <span>Analysis generated using advanced AI models</span>
      </div>
    </div>
  );
}

/**
 * Main App Component
 */

import React, { useState } from 'react';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import { ChartContainer } from './components/ChartContainer';
import { getROCCurveOptions, getConfusionMatrixOptions } from './charts';
import type { ROCCurveData, ConfusionMatrixData, Account } from './types';

// Dashboard Content Component
function DashboardContent() {
  const { state, loadCSVData } = useDashboard();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleLoadData = async () => {
    if (selectedFile) {
      try {
        await loadCSVData(selectedFile);
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    }
  };

  // Mock data for demonstration
  const mockROCData: ROCCurveData = {
    fpr: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    tpr: [0, 0.3, 0.5, 0.7, 0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 1.0],
    auc: 0.8765,
    thresholds: [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
  };

  const mockConfusionData: ConfusionMatrixData = {
    matrix: [
      [850, 50],
      [30, 70],
    ],
    labels: ['Normal', 'Fraud'],
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Financial Risk Dashboard
          </h1>
          <p className="text-gray-600">
            Crypto Suspicious Account Detection System
          </p>
        </header>

        {/* File Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Data Source</h2>
          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            <button
              onClick={handleLoadData}
              disabled={!selectedFile || state.loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md
                hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                transition-colors"
            >
              {state.loading ? 'Loading...' : 'Load Data'}
            </button>
          </div>
          {state.error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{state.error}</p>
            </div>
          )}
          {state.lastUpdated && (
            <div className="mt-4 text-sm text-gray-600">
              Last updated: {state.lastUpdated.toLocaleString()}
            </div>
          )}
        </div>

        {/* KPI Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Accounts</h3>
            <p className="text-3xl font-bold text-gray-900">{state.accounts.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">High Risk</h3>
            <p className="text-3xl font-bold text-red-600">
              {state.accounts.filter((a: Account) => a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Risk Ratio</h3>
            <p className="text-3xl font-bold text-orange-600">
              {state.accounts.length > 0
                ? ((state.accounts.filter((a: Account) => a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL').length / state.accounts.length) * 100).toFixed(1)
                : '0.0'}%
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Avg Risk Score</h3>
            <p className="text-3xl font-bold text-blue-600">
              {state.accounts.length > 0
                ? (state.accounts.reduce((sum: number, a: Account) => sum + a.risk_score, 0) / state.accounts.length).toFixed(1)
                : '0.0'}
            </p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <ChartContainer
            title="ROC Curve"
            options={getROCCurveOptions(state.charts.roc_curve || mockROCData)}
            height={400}
          />
          <ChartContainer
            title="Confusion Matrix"
            options={getConfusionMatrixOptions(state.charts.confusion_matrix || mockConfusionData)}
            height={400}
          />
        </div>

        {/* Account List Section */}
        {state.accounts.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Account List</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Account ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Reason
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {state.accounts.slice(0, 10).map((account: Account) => (
                    <tr key={account.account_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {account.account_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {account.risk_score.toFixed(1)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                          ${account.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                            account.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                            account.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'}`}>
                          {account.risk_level}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {account.risk_reason || account.explanation}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Main App Component with Provider
export default function App() {
  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}

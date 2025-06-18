import React, { useState, useEffect, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import './MonitoringPage.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const MonitoringPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [qualitySummary, setQualitySummary] = useState(null);
  const [performanceSummary, setPerformanceSummary] = useState(null);
  const [queryPatterns, setQueryPatterns] = useState(null);
  const [recentMetrics, setRecentMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  // API call function with error handling
  const fetchWithAuth = async (url) => {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  };

  // Fetch all monitoring data
  const fetchMonitoringData = useCallback(async () => {
    try {
      setError(null);
      
      // Parallel fetch all monitoring endpoints
      const [
        dashboardRes,
        healthRes,
        qualityRes,
        performanceRes,
        patternsRes,
        recentRes
      ] = await Promise.all([
        fetchWithAuth('/api/monitoring/dashboard?hours=24'),
        fetchWithAuth('/api/monitoring/system/health'),
        fetchWithAuth('/api/monitoring/quality/summary'),
        fetchWithAuth('/api/monitoring/performance/summary?period=24h'),
        fetchWithAuth('/api/monitoring/patterns/queries?hours=24'),
        fetchWithAuth('/api/monitoring/quality/recent?limit=50')
      ]);

      setDashboardData(dashboardRes);
      setSystemHealth(healthRes);
      setQualitySummary(qualityRes);
      setPerformanceSummary(performanceRes);
      setQueryPatterns(patternsRes);
      setRecentMetrics(recentRes);
      setLastUpdate(new Date());
      setIsLoading(false);
    } catch (err) {
      console.error('Error fetching monitoring data:', err);
      setError(err.message);
      setIsLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchMonitoringData();
  }, [fetchMonitoringData]);

  // Auto-refresh setup
  useEffect(() => {
    let interval;
    if (autoRefresh && !isLoading) {
      interval = setInterval(() => {
        fetchMonitoringData();
      }, refreshInterval * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval, fetchMonitoringData, isLoading]);

  // Get health status color
  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'excellent': return '#00ff88';
      case 'good': return '#4ade80';
      case 'fair': return '#fbbf24';
      case 'poor': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Get health status icon
  const getHealthStatusIcon = (status) => {
    switch (status) {
      case 'excellent': return '🟢';
      case 'good': return '🟡';
      case 'fair': return '🟠';
      case 'poor': return '🔴';
      default: return '⚪';
    }
  };

  // Export data functions
  const exportToJSON = () => {
    const exportData = {
      dashboard: dashboardData,
      systemHealth,
      qualitySummary,
      performanceSummary,
      queryPatterns,
      recentMetrics,
      exportTimestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `monitoring-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    if (!recentMetrics?.metrics) return;
    
    const csvHeaders = [
      'Timestamp',
      'Query',
      'Processing Time',
      'Quality Score',
      'Confidence Score',
      'Retrieval Method',
      'Error Occurred'
    ];
    
    const csvRows = recentMetrics.metrics.map(metric => [
      metric.timestamp,
      `"${metric.query || 'N/A'}"`,
      metric.processing_time || 0,
      metric.answer_quality_score || 0,
      metric.confidence_score || 0,
      metric.retrieval_method || 'N/A',
      metric.error_occurred || false
    ]);
    
    const csvContent = [csvHeaders, ...csvRows]
      .map(row => row.join(','))
      .join('\n');
    
    const dataBlob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `monitoring-metrics-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Chart configurations
  const getPerformanceTrendChart = () => {
    if (!dashboardData?.performance_trends) return null;

    const trends = dashboardData.performance_trends.slice(-24); // Last 24 hours
    
    return {
      labels: trends.map(t => t.hour || 'N/A'),
      datasets: [
        {
          label: 'Response Time (s)',
          data: trends.map(t => t.avg_processing_time || 0),
          borderColor: '#00ff88',
          backgroundColor: 'rgba(0, 255, 136, 0.1)',
          tension: 0.4,
          yAxisID: 'y',
        },
        {
          label: 'Success Rate (%)',
          data: trends.map(t => t.success_rate || 0),
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.1)',
          tension: 0.4,
          yAxisID: 'y1',
        }
      ]
    };
  };

  const getQualityTrendChart = () => {
    if (!dashboardData?.performance_trends) return null;

    const trends = dashboardData.performance_trends.slice(-24);
    
    return {
      labels: trends.map(t => t.hour || 'N/A'),
      datasets: [
        {
          label: 'Quality Score',
          data: trends.map(t => t.avg_quality_score || 0),
          borderColor: '#c27cb9',
          backgroundColor: 'rgba(194, 124, 185, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Confidence Score',
          data: trends.map(t => t.avg_confidence_score || 0),
          borderColor: '#fbbf24',
          backgroundColor: 'rgba(251, 191, 36, 0.1)',
          tension: 0.4,
        }
      ]
    };
  };

  const getQueryPatternsChart = () => {
    if (!queryPatterns?.query_patterns) return null;

    const patterns = queryPatterns.query_patterns;
    const labels = Object.keys(patterns);
    const data = Object.values(patterns);
    
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            '#00ff88',
            '#c27cb9',
            '#4ade80',
            '#fbbf24',
            '#ef4444',
            '#3b82f6',
          ],
          borderColor: '#1a1a1a',
          borderWidth: 2,
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e5e7eb',
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' }
      }
    }
  };

  const dualAxisChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e5e7eb',
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        ticks: { color: '#9ca3af' },
        grid: { drawOnChartArea: false }
      }
    }
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#e5e7eb',
          padding: 20
        }
      }
    }
  };

  if (isLoading) {
    return (
      <div className="monitoring-page">
        <div className="monitoring-loading">
          <div className="loading-spinner"></div>
          <p>Loading monitoring dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="monitoring-page">
        <div className="monitoring-error">
          <h2>⚠️ Error Loading Monitoring Data</h2>
          <p>{error}</p>
          <button onClick={fetchMonitoringData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="monitoring-page">
      <div className="monitoring-header">
        <div className="header-left">
          <h1>🚀 System Monitoring Dashboard</h1>
          <p>Real-time performance analytics and system health monitoring</p>
        </div>
        <div className="header-controls">
          <div className="refresh-controls">
            <label>
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto-refresh
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
            >
              <option value={15}>15s</option>
              <option value={30}>30s</option>
              <option value={60}>1m</option>
              <option value={120}>2m</option>
            </select>
          </div>
          <div className="export-controls">
            <button onClick={exportToJSON} className="export-btn">
              Export JSON
            </button>
            <button onClick={exportToCSV} className="export-btn">
              Export CSV
            </button>
          </div>
          <div className="last-update">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* System Health Status Cards */}
      <div className="health-status-section">
        <div className="health-card main-health">
          <div className="health-indicator">
            <span className="health-icon">
              {getHealthStatusIcon(systemHealth?.health_status)}
            </span>
            <div className="health-info">
              <h3>System Health</h3>
              <span 
                className="health-status"
                style={{ color: getHealthStatusColor(systemHealth?.health_status) }}
              >
                {systemHealth?.health_status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
          </div>
        </div>

        <div className="health-metrics-grid">
          <div className="metric-card">
            <h4>Success Rate</h4>
            <div className="metric-value">
              {systemHealth?.metrics?.success_rate?.toFixed(1) || 0}%
            </div>
          </div>
          <div className="metric-card">
            <h4>Avg Response Time</h4>
            <div className="metric-value">
              {systemHealth?.metrics?.avg_response_time?.toFixed(2) || 0}s
            </div>
          </div>
          <div className="metric-card">
            <h4>Quality Score</h4>
            <div className="metric-value">
              {systemHealth?.metrics?.avg_quality_score?.toFixed(2) || 0}/5
            </div>
          </div>
          <div className="metric-card">
            <h4>Total Queries</h4>
            <div className="metric-value">
              {systemHealth?.metrics?.total_queries || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Analytics */}
      <div className="analytics-section">
        <div className="chart-container">
          <h3>📈 Performance Trends (24h)</h3>
          {getPerformanceTrendChart() && (
            <div className="chart-wrapper">
              <Line data={getPerformanceTrendChart()} options={dualAxisChartOptions} />
            </div>
          )}
        </div>

        <div className="chart-container">
          <h3>🎯 Answer Quality Trends</h3>
          {getQualityTrendChart() && (
            <div className="chart-wrapper">
              <Line data={getQualityTrendChart()} options={chartOptions} />
            </div>
          )}
        </div>
      </div>

      {/* Query Analytics */}
      <div className="analytics-section">
        <div className="chart-container">
          <h3>🔍 Query Pattern Analysis</h3>
          {getQueryPatternsChart() && (
            <div className="chart-wrapper">
              <Pie data={getQueryPatternsChart()} options={pieChartOptions} />
            </div>
          )}
        </div>

        <div className="popular-queries">
          <h3>🔥 Popular Queries</h3>
          <div className="query-list">
            {queryPatterns?.popular_queries?.slice(0, 10).map((query, index) => (
              <div key={index} className="query-item">
                <span className="query-text">"{query.query}"</span>
                <span className="query-count">{query.count} times</span>
              </div>
            )) || <p>No query data available</p>}
          </div>
        </div>
      </div>

      {/* Detailed Metrics Table */}
      <div className="metrics-table-section">
        <h3>📊 Recent Query Metrics</h3>
        <div className="table-container">
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Query</th>
                <th>Response Time</th>
                <th>Quality Score</th>
                <th>Confidence</th>
                <th>Method</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentMetrics?.metrics?.slice(0, 20).map((metric, index) => (
                <tr key={index}>
                  <td>{new Date(metric.timestamp).toLocaleTimeString()}</td>
                  <td className="query-cell">
                    {metric.query ? `"${metric.query.substring(0, 50)}${metric.query.length > 50 ? '...' : ''}"` : 'N/A'}
                  </td>
                  <td>{metric.processing_time?.toFixed(2) || 0}s</td>
                  <td>
                    <span className={`score ${metric.answer_quality_score >= 4 ? 'excellent' : metric.answer_quality_score >= 3 ? 'good' : 'poor'}`}>
                      {metric.answer_quality_score?.toFixed(2) || 0}/5
                    </span>
                  </td>
                  <td>{(metric.confidence_score * 100)?.toFixed(0) || 0}%</td>
                  <td>{metric.retrieval_method || 'N/A'}</td>
                  <td>
                    <span className={`status ${metric.error_occurred ? 'error' : 'success'}`}>
                      {metric.error_occurred ? '❌' : '✅'}
                    </span>
                  </td>
                </tr>
              )) || (
                <tr>
                  <td colSpan="7">No recent metrics available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Active Alerts */}
      {dashboardData?.active_alerts?.length > 0 && (
        <div className="alerts-section">
          <h3>⚠️ Active Alerts</h3>
          <div className="alerts-list">
            {dashboardData.active_alerts.map((alert, index) => (
              <div key={index} className={`alert-item ${alert.severity}`}>
                <div className="alert-icon">
                  {alert.severity === 'high' ? '🚨' : alert.severity === 'medium' ? '⚠️' : 'ℹ️'}
                </div>
                <div className="alert-content">
                  <h4>{alert.type}</h4>
                  <p>{alert.message}</p>
                  <small>{new Date(alert.timestamp).toLocaleString()}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MonitoringPage; 
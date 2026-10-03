import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  AlertTriangle,
  TrendingDown,
  Users,
  CheckCircle2,
  Bell,
  ArrowRight,
  ShieldAlert,
  BrainCircuit,
  Filter,
  Download,
  Loader2,
  RefreshCw,
  AlertCircle,
  BookOpen
} from 'lucide-react';
import Card, { StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Select from '../../components/common/Select';
import { aiInsightsService } from '../../services/aiInsightsService';

export function AIInsights() {
  const navigate = useNavigate();
  const [filterSeverity, setFilterSeverity] = useState('All');
  const [summaryData, setSummaryData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const fetchInsights = useCallback(async () => {
    setIsLoading(true);
    setApiError(null);

    try {
      const params = {};
      if (filterSeverity !== 'All') {
        params.risk_level = filterSeverity.toUpperCase();
      }

      const res = await aiInsightsService.getInstitutionalInsights(params);
      setSummaryData(res);
    } catch (err) {
      setApiError(err.message || 'Unable to fetch student risk analysis.');
    } finally {
      setIsLoading(false);
    }
  }, [filterSeverity]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const showNotification = (message) => {
    setFeedback(message);
    setTimeout(() => setFeedback(null), 4000);
  };

  const insightsList = summaryData?.items || [];
  const totalAnalyzed = summaryData?.total_students_analyzed || 0;
  const criticalCount = summaryData?.critical_count || 0;
  const highCount = summaryData?.high_count || 0;
  const mediumCount = summaryData?.medium_count || 0;
  const lowCount = summaryData?.low_count || 0;
  const avgRisk = summaryData?.average_risk_score || 0.0;

  const getRiskBadgeVariant = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'error';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
      default:
        return 'success';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-indigo-950 via-slate-900 to-blue-950 text-white p-6 sm:p-8 rounded-2xl shadow-soft">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-tertiary-fixed border border-white/15 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            Deterministic Academic Intelligence
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
            Student Academic Risk Radar & Diagnostic Insights
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1.5 max-w-2xl">
            Rule-based intelligence engine analyzes attendance consistency, assessment failure rates, and score trajectories from MongoDB to guide timely academic interventions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="bg-white/10 text-white border-white/20 hover:bg-white/20"
            icon={RefreshCw}
            onClick={fetchInsights}
            disabled={isLoading}
          >
            Re-evaluate
          </Button>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-3 text-tertiary text-xs sm:text-sm animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span className="font-semibold">{feedback}</span>
        </div>
      )}

      {/* Error Banner */}
      {apiError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-error text-xs sm:text-sm animate-in fade-in">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="font-semibold">{apiError}</span>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Critical & High Risk"
          value={`${criticalCount + highCount} Students`}
          change={`${criticalCount} Critical`}
          trend="alert"
          period="Attendance / Score Deficit"
          icon={AlertTriangle}
          color="error"
        />
        <StatCard
          title="Medium Risk Alert"
          value={`${mediumCount} Students`}
          change="Moderate Alert"
          trend="neutral"
          period="Under Performance Watch"
          icon={ShieldAlert}
          color="warning"
        />
        <StatCard
          title="Low Risk / On-Track"
          value={`${lowCount} Students`}
          change="Consistent"
          trend="up"
          period="Good Academic Standing"
          icon={CheckCircle2}
          color="tertiary"
        />
        <StatCard
          title="Average Risk Score"
          value={`${avgRisk} / 100`}
          change={`${totalAnalyzed} Evaluated`}
          trend="neutral"
          period="Institutional Risk Index"
          icon={BrainCircuit}
          color="primary"
        />
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-on-surface uppercase tracking-wider">Filter Risk Band:</span>
          <div className="flex flex-wrap gap-1.5">
            {['All', 'Critical', 'High', 'Medium', 'Low'].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  filterSeverity.toLowerCase() === sev.toLowerCase()
                    ? 'bg-primary text-white shadow-xs'
                    : 'bg-surface-container text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>
        <span className="text-xs text-on-surface-variant hidden sm:inline">
          Showing {insightsList.length} Analyzed Student{insightsList.length === 1 ? '' : 's'}
        </span>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20 text-on-surface-variant space-y-2">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <p className="text-xs font-semibold">Computing academic risk models across student profiles...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && insightsList.length === 0 && (
        <div className="py-16 text-center space-y-3 bg-surface-container-lowest border border-outline-variant/60 rounded-2xl shadow-soft">
          <BrainCircuit className="w-10 h-10 text-on-surface-variant/40 mx-auto" />
          <p className="text-sm font-semibold text-on-surface">No student risk records matching selected criteria.</p>
          <p className="text-xs text-on-surface-variant max-w-sm mx-auto">
            All students in the selected risk band have good academic indicators.
          </p>
        </div>
      )}

      {/* Insight Alert Cards */}
      {!isLoading && (
        <div className="space-y-4">
          {insightsList.map((insight) => (
            <div
              key={insight.student_id}
              className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 shadow-soft hover:shadow-card transition-all space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-outline-variant/30 pb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                      insight.risk_level === 'CRITICAL' || insight.risk_level === 'HIGH'
                        ? 'bg-red-50 text-error'
                        : insight.risk_level === 'MEDIUM'
                        ? 'bg-amber-50 text-amber-700'
                        : 'bg-emerald-50 text-tertiary'
                    }`}
                  >
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm sm:text-base text-on-surface">
                      {insight.student_name}
                    </h3>
                    <p className="text-xs text-on-surface-variant">
                      {insight.department} • Year {insight.year} • Roll No: {insight.roll_number}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant={getRiskBadgeVariant(insight.risk_level)} size="md">
                    {insight.risk_level} Risk
                  </Badge>
                  <span className="text-xs font-bold text-primary bg-primary/10 px-2.5 py-1 rounded-lg">
                    Risk Index: {insight.risk_score} / 100
                  </span>
                </div>
              </div>

              {/* Attendance & Academic Quick Metrics Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-surface-container-low/60 p-3 rounded-xl text-xs">
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Attendance</span>
                  <span className={`font-bold ${insight.attendance_percentage < 75 ? 'text-error' : 'text-on-surface'}`}>
                    {insight.attendance_percentage}% ({insight.total_attendance_days} sessions)
                  </span>
                </div>
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Academic Score</span>
                  <span className={`font-bold ${insight.academic_percentage < 50 ? 'text-error' : 'text-on-surface'}`}>
                    {insight.academic_percentage}% ({insight.total_assessments} tests)
                  </span>
                </div>
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Failed Assessments</span>
                  <span className={`font-bold ${insight.failed_assessments > 0 ? 'text-error' : 'text-tertiary'}`}>
                    {insight.failed_assessments} failed
                  </span>
                </div>
                <div>
                  <span className="text-on-surface-variant block text-[10px] uppercase font-bold">Status</span>
                  <span className="font-bold text-primary">
                    {insight.risk_level === 'LOW' ? 'Safe Zone' : 'Intervention Needed'}
                  </span>
                </div>
              </div>

              {/* Diagnostic Factors & Recommendations */}
              <div className="space-y-2 text-xs sm:text-sm">
                <div>
                  <strong className="text-on-surface block mb-1">Diagnostic Factors:</strong>
                  <ul className="list-disc list-inside text-xs text-on-surface-variant space-y-0.5">
                    {insight.key_factors.map((factor, idx) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-xl text-xs text-blue-900">
                  <strong className="block mb-1">Recommended Action Plan:</strong>
                  <ul className="list-disc list-inside space-y-0.5">
                    {insight.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-end gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/students/${insight.student_id}`)}
                >
                  View Academic Record
                </Button>
                <Button
                  variant="container"
                  size="sm"
                  icon={Bell}
                  onClick={() => showNotification(`Counseling alert logged for ${insight.student_name} (${insight.roll_number}).`)}
                >
                  Trigger Faculty Counseling
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AIInsights;

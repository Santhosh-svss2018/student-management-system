import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  GraduationCap,
  CalendarCheck,
  TrendingUp,
  UserPlus,
  FileDown,
  Sparkles,
  ArrowRight,
  BookOpen,
  Award,
  AlertTriangle,
  Building2,
  Loader2,
  RefreshCw
} from 'lucide-react';
import Card, { StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { useAuth } from '../../context/AuthContext';
import { analyticsService } from '../../services/analyticsService';

export function AdminDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [overview, setOverview] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [overviewData, deptData] = await Promise.all([
        analyticsService.getAdminOverview(),
        analyticsService.getAdminDepartments(),
      ]);
      setOverview(overviewData);
      setDepartments(deptData?.departments || []);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to load live institutional analytics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const deptColors = [
    'bg-blue-600',
    'bg-emerald-600',
    'bg-indigo-600',
    'bg-amber-600',
    'bg-rose-600',
    'bg-purple-600',
  ];

  const totalStudents = overview ? overview.total_students : 0;
  const activeStudents = overview ? overview.active_students : 0;
  const totalTeachers = overview ? overview.total_teachers : 0;
  const avgAttendance = overview ? `${overview.overall_attendance_percentage}%` : '0.0%';
  const avgAcademic = overview ? `${overview.overall_academic_percentage}%` : '0.0%';
  const atRiskCount = overview ? overview.students_at_risk : 0;

  const displayName = user?.name || user?.full_name || 'Dr. Sarah Jenkins';

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-primary-container via-primary to-[#003da8] text-white p-6 sm:p-8 rounded-2xl shadow-soft relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white border border-white/20 mb-3">
            <Building2 className="w-3.5 h-3.5" />
            University Administration Portal
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome, {displayName}
          </h1>
          <p className="text-xs sm:text-sm text-blue-100 mt-1.5 max-w-xl">
            {overview
              ? `Real-time institutional metrics. ${activeStudents} active students enrolled across ${departments.length} departments.`
              : 'Institutional overview and live system metrics from MongoDB database.'}
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10">
          <Button
            variant="outline"
            size="md"
            className="bg-white/10 hover:bg-white/20 text-white border-white/30"
            icon={FileDown}
            onClick={() => navigate('/admin/reports')}
          >
            Export Reports
          </Button>
          <Button
            variant="white"
            size="md"
            icon={UserPlus}
            onClick={() => navigate('/students/new')}
          >
            Add Student
          </Button>
        </div>
      </div>

      {/* Loading Notice */}
      {isLoading && (
        <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-xs flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <Loader2 className="w-4 h-4 text-primary animate-spin" />
          <span>Synchronizing live metrics and department analytics from MongoDB...</span>
        </div>
      )}

      {/* Error State */}
      {errorMessage && !isLoading && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between gap-3 text-amber-900 text-xs">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={fetchDashboardData}>
            Retry
          </Button>
        </div>
      )}

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="Total Enrolled Students"
          value={totalStudents.toLocaleString()}
          change={`${activeStudents} Active`}
          trend="up"
          period="in MongoDB database"
          icon={Users}
          color="primary"
        />
        <StatCard
          title="Active Faculty Members"
          value={totalTeachers.toLocaleString()}
          change="Verified Staff"
          trend="up"
          period="teaching faculty"
          icon={GraduationCap}
          color="tertiary"
        />
        <StatCard
          title="Average Attendance"
          value={avgAttendance}
          change={overview && overview.attendance_distribution ? `${overview.attendance_distribution.present} Present` : 'Real-time'}
          trend="up"
          period="across active sessions"
          icon={CalendarCheck}
          color="secondary"
        />
        <StatCard
          title="Overall Academic Average"
          value={avgAcademic}
          change={overview ? `${overview.total_marks_records} Recorded` : 'Evaluations'}
          trend="up"
          period="curriculum assessments"
          icon={Award}
          color="primary"
        />
      </div>

      {/* Main Grid: Department Matrix & AI Insights Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Department Performance */}
        <div className="lg:col-span-8 space-y-6">
          <Card
            title="Department Enrollment & Attendance Matrix"
            subtitle="Live breakdown across academic departments from database"
            headerAction={
              <Button variant="ghost" size="sm" onClick={() => navigate('/admin/reports')}>
                View Details
              </Button>
            }
          >
            {departments.length === 0 ? (
              <div className="py-8 text-center text-xs text-on-surface-variant space-y-1">
                <Building2 className="w-8 h-8 mx-auto text-outline" />
                <p className="font-semibold text-on-surface">No departments recorded yet.</p>
                <p>Enrolling students will automatically populate department metrics.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {departments.map((dept, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/40 hover:bg-surface-container-low transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div>
                        <h4 className="font-semibold text-sm text-on-surface">{dept.department}</h4>
                        <p className="text-xs text-on-surface-variant">
                          {dept.student_count} Enrolled • Avg Academic Score: {dept.academic_percentage}%
                          {dept.at_risk_count > 0 && ` • ${dept.at_risk_count} At-Risk`}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className="text-xs font-semibold text-on-surface">Attendance: {dept.attendance_percentage}%</span>
                        </div>
                        <Badge variant={dept.at_risk_count > 0 ? 'warning' : 'success'} size="sm">
                          {dept.at_risk_count > 0 ? `${dept.at_risk_count} Flagged` : 'Healthy'}
                        </Badge>
                      </div>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                      <div
                        className={`h-full ${deptColors[idx % deptColors.length]} rounded-full transition-all duration-500`}
                        style={{ width: `${Math.min(100, dept.attendance_percentage)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Quick Shortcuts */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div
              onClick={() => navigate('/students')}
              className="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/60 hover:border-primary hover:shadow-card cursor-pointer transition-all duration-150 flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-primary flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-on-surface">Student Directory</h4>
                <p className="text-xs text-on-surface-variant">{totalStudents} Total Records</p>
              </div>
            </div>

            <div
              onClick={() => navigate('/teacher/attendance')}
              className="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/60 hover:border-primary hover:shadow-card cursor-pointer transition-all duration-150 flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-tertiary flex items-center justify-center">
                <CalendarCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-on-surface">Attendance Portal</h4>
                <p className="text-xs text-on-surface-variant">Session tracking</p>
              </div>
            </div>

            <div
              onClick={() => navigate('/ai/insights')}
              className="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/60 hover:border-primary hover:shadow-card cursor-pointer transition-all duration-150 flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-on-surface">AI Risk Radar</h4>
                <p className="text-xs text-on-surface-variant">{atRiskCount} Flagged Alerts</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right 4 Cols: AI Alert Widget & Recent Quick Info */}
        <div className="lg:col-span-4 space-y-6">
          {/* AI Early Warning Banner */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-900 via-blue-900 to-[#1e1b4b] text-white shadow-soft relative overflow-hidden">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-tertiary-fixed">
              <Sparkles className="w-4 h-4" />
              <span>AI Academic Forecaster</span>
            </div>
            <h3 className="font-display text-lg font-bold mt-2">
              {atRiskCount > 0 ? `${atRiskCount} Students Requiring Attention` : 'All Students in Safe Academic Standing'}
            </h3>
            <p className="text-xs text-blue-200 mt-1 leading-relaxed">
              {atRiskCount > 0
                ? `${overview?.high_risk_students || 0} high-risk and ${overview?.critical_risk_students || 0} critical-risk students flagged by multi-factor academic & attendance monitoring.`
                : 'Zero critical risk alerts detected across active department cohorts.'}
            </p>
            <Button
              variant="container"
              size="sm"
              className="mt-4 bg-tertiary-fixed text-[#002113] hover:bg-emerald-300 font-bold w-full"
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => navigate('/ai/insights')}
            >
              Review Intervention List
            </Button>
          </div>

          {/* Institutional Grade Distribution Card */}
          <Card title="Grade Distribution Overview" subtitle="Consolidated academic marks spread">
            {overview && overview.grade_distribution ? (
              <div className="space-y-2.5">
                {Object.entries(overview.grade_distribution).map(([grade, count]) => {
                  const total = overview.total_marks_records || 1;
                  const pct = Math.round((count / total) * 100);
                  return (
                    <div key={grade} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-on-surface">Grade {grade}</span>
                        <span className="text-on-surface-variant">{count} Evaluations ({pct}%)</span>
                      </div>
                      <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            grade === 'A+' ? 'bg-emerald-500' :
                            grade === 'A' ? 'bg-blue-600' :
                            grade === 'B' ? 'bg-indigo-500' :
                            grade === 'C' ? 'bg-amber-500' : 'bg-red-500'
                          } rounded-full`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="py-4 text-center text-xs text-on-surface-variant">
                No marks evaluated yet.
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;

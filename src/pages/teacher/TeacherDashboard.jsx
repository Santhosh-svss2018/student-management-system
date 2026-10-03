import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  CalendarCheck,
  Award,
  Clock,
  MapPin,
  Users,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
  TrendingUp
} from 'lucide-react';
import Card, { StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { useAuth } from '../../context/AuthContext';
import { analyticsService } from '../../services/analyticsService';
import { marksService } from '../../services/marksService';

export function TeacherDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [teacherAnalytics, setTeacherAnalytics] = useState(null);
  const [recentMarks, setRecentMarks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [overviewData, marksRes] = await Promise.all([
        analyticsService.getTeacherOverview(user?.department || ''),
        marksService.getMarks({ limit: 4 }),
      ]);
      setTeacherAnalytics(overviewData);
      setRecentMarks(marksRes?.items || []);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to load live faculty analytics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const todayClasses = [
    {
      code: 'CS-301',
      title: 'Design & Analysis of Algorithms',
      time: '10:00 AM - 11:30 AM',
      room: 'Lecture Hall 302',
      batch: 'B.Tech CS 6th Sem (Sec A)',
      students: teacherAnalytics ? teacherAnalytics.student_count : 64,
      status: 'Upcoming',
      isNext: true,
    },
    {
      code: 'CS-402',
      title: 'Cloud Architecture & DevOps',
      time: '02:00 PM - 03:30 PM',
      room: 'Advanced Computing Lab 4',
      batch: 'B.Tech CS 8th Sem (Sec B)',
      students: teacherAnalytics ? teacherAnalytics.student_count : 48,
      status: 'Scheduled',
      isNext: false,
    },
  ];

  const studentCount = teacherAnalytics ? teacherAnalytics.student_count : 0;
  const attendanceRate = teacherAnalytics?.attendance_overview?.attendance_percentage
    ? `${teacherAnalytics.attendance_overview.attendance_percentage}%`
    : '0.0%';
  const academicRate = teacherAnalytics?.academic_performance?.overall_percentage
    ? `${teacherAnalytics.academic_performance.overall_percentage}%`
    : '0.0%';
  const evaluationsCount = teacherAnalytics?.academic_performance?.total_evaluations || 0;
  const attentionList = teacherAnalytics?.students_requiring_attention || [];
  const defaultersList = teacherAnalytics?.attendance_defaulters || [];

  const displayName = user?.name || user?.full_name || 'Prof. Marcus Vance';
  const displayDept = user?.department || 'Computer Science & Engineering';

  return (
    <div className="space-y-6">
      {/* Faculty Hero Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-primary via-[#003da8] to-[#002670] text-white p-6 sm:p-8 rounded-2xl shadow-soft">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white border border-white/20 mb-3">
            <BookOpen className="w-3.5 h-3.5" />
            Faculty Academic Portal
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome, {displayName}
          </h1>
          <p className="text-xs sm:text-sm text-blue-100 mt-1.5 max-w-xl">
            Department of {displayDept} • {studentCount} Students Enrolled • Real-time teaching & attendance telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="white"
            size="md"
            icon={CalendarCheck}
            onClick={() => navigate('/teacher/attendance')}
          >
            Mark Attendance
          </Button>
          <Button
            variant="outline"
            size="md"
            className="bg-white/10 hover:bg-white/20 text-white border-white/30"
            icon={Award}
            onClick={() => navigate('/teacher/marks')}
          >
            Enter Marks
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-xs flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <Loader2 className="w-4 h-4 text-primary animate-spin" />
          <span>Synchronizing student records, attendance logs, and marks evaluations...</span>
        </div>
      )}

      {/* Error State */}
      {errorMessage && !isLoading && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0" />
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
          title="Enrolled Cohort"
          value={studentCount.toLocaleString()}
          change="Active Roster"
          trend="neutral"
          period={displayDept}
          icon={Users}
          color="primary"
        />
        <StatCard
          title="Class Avg. Attendance"
          value={attendanceRate}
          change={teacherAnalytics?.attendance_overview ? `${teacherAnalytics.attendance_overview.present_count} Attended` : 'Live telemetry'}
          trend="up"
          period="Across logged sessions"
          icon={CalendarCheck}
          color="tertiary"
        />
        <StatCard
          title="Academic Performance"
          value={academicRate}
          change={teacherAnalytics?.academic_performance ? `${teacherAnalytics.academic_performance.pass_percentage}% Pass Rate` : 'Average Score'}
          trend="up"
          period="Evaluated assessments"
          icon={Award}
          color="secondary"
        />
        <StatCard
          title="Completed Evaluations"
          value={evaluationsCount.toLocaleString()}
          change={`${attentionList.length} Attention Flags`}
          trend={attentionList.length > 0 ? 'alert' : 'up'}
          period="Database records"
          icon={TrendingUp}
          color={attentionList.length > 0 ? 'error' : 'primary'}
        />
      </div>

      {/* Main Grid: Today's Timetable & Attention Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Schedule & Recent Evaluations */}
        <div className="lg:col-span-8 space-y-6">
          <Card
            title="Today's Academic Schedule"
            subtitle="Scheduled lectures and laboratory sessions for today"
            headerAction={<Badge variant="primary" size="sm">2 Sessions Today</Badge>}
          >
            <div className="space-y-4">
              {todayClasses.map((cls, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all ${
                    cls.isNext
                      ? 'bg-primary/5 border-primary/40 ring-1 ring-primary/20'
                      : 'bg-surface-container-low/70 border-outline-variant/40'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs px-2 py-0.5 rounded bg-primary-container text-white">
                          {cls.code}
                        </span>
                        <h4 className="font-bold text-sm sm:text-base text-on-surface">{cls.title}</h4>
                      </div>
                      <p className="text-xs text-on-surface-variant mt-1">{cls.batch}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant={cls.isNext ? 'primary' : 'outline'}
                        size="sm"
                        icon={CalendarCheck}
                        onClick={() => navigate('/teacher/attendance')}
                      >
                        Take Attendance
                      </Button>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 mt-3 pt-3 border-t border-outline-variant/30 text-xs text-on-surface-variant">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-primary" />
                      <span>{cls.time}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-tertiary" />
                      <span>{cls.room}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-secondary" />
                      <span>{cls.students} Enrolled Students</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Evaluations Posted */}
          <Card
            title="Recent Assessment Postings"
            subtitle="Authoritative evaluation scores recorded in MongoDB"
            headerAction={
              <Button variant="ghost" size="sm" onClick={() => navigate('/teacher/marks')}>
                Manage All Marks
              </Button>
            }
          >
            {recentMarks.length === 0 ? (
              <div className="py-6 text-center text-xs text-on-surface-variant">
                No evaluation marks entered yet. Click "Enter Marks" to record scores.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {recentMarks.map((m) => (
                  <div key={m.marks_id} className="p-3 rounded-xl bg-surface-container-low/60 border border-outline-variant/40 flex justify-between items-center">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-xs text-primary">{m.subject_code}</span>
                        <Badge variant="outline" size="sm">Sem {m.semester}</Badge>
                      </div>
                      <p className="font-semibold text-xs text-on-surface mt-1">{m.student_id}</p>
                      <p className="text-[11px] text-on-surface-variant">{m.subject_name}</p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-xs text-on-surface">{m.marks_obtained}/{m.max_marks}</span>
                      <span className="block font-bold text-[11px] text-primary">Grade {m.grade} ({m.percentage}%)</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right 4 Cols: Attention List & Tools */}
        <div className="lg:col-span-4 space-y-6">
          {/* Students Requiring Attention */}
          <Card
            title="Students Requiring Attention"
            subtitle="Academic risk flags & low attendance (<75%)"
          >
            <div className="space-y-3">
              {attentionList.length === 0 && defaultersList.length === 0 ? (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>All students are maintaining safe attendance and performance thresholds.</span>
                </div>
              ) : (
                <>
                  {attentionList.slice(0, 3).map((item) => (
                    <div key={item.student_id} className="p-3 rounded-xl bg-rose-50/70 border border-rose-200/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-950">{item.student_name}</span>
                        <Badge variant="error" size="sm">{item.risk_level}</Badge>
                      </div>
                      <p className="text-[11px] text-rose-800 mt-1">{item.reason}</p>
                      <div className="flex justify-between items-center mt-2 pt-1.5 border-t border-rose-200/50 text-[10px] text-rose-900 font-semibold">
                        <span>Attendance: {item.attendance_percentage}%</span>
                        <span>Academic: {item.academic_percentage}%</span>
                      </div>
                    </div>
                  ))}

                  {defaultersList.slice(0, 2).map((def) => (
                    <div key={def.student_id} className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-amber-950">{def.student_name}</span>
                        <Badge variant="warning" size="sm">Defaulter</Badge>
                      </div>
                      <p className="text-[11px] text-amber-800 mt-1">
                        Attendance is critically low at {def.attendance_percentage}% ({def.present_days}/{def.total_days} sessions).
                      </p>
                    </div>
                  ))}
                </>
              )}
            </div>
          </Card>

          {/* Quick Class Admin Tools */}
          <Card title="Class Administration" subtitle="Direct tools for course instructors">
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start text-xs"
                icon={Users}
                onClick={() => navigate('/students')}
              >
                Browse Student Directory ({studentCount})
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start text-xs"
                icon={CalendarCheck}
                onClick={() => navigate('/teacher/attendance')}
              >
                Historical Attendance Logs
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start text-xs"
                icon={Sparkles}
                onClick={() => navigate('/ai/insights')}
              >
                View Institutional AI Insights
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default TeacherDashboard;

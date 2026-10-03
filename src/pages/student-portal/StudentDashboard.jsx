import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  CalendarCheck,
  Award,
  BookOpen,
  Clock,
  MapPin,
  Bot,
  Sparkles,
  ArrowRight,
  Download,
  AlertCircle,
  Loader2,
  RefreshCw,
  CheckCircle2,
  FileText
} from 'lucide-react';
import Card, { StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { useAuth } from '../../context/AuthContext';
import { studentService } from '../../services/studentService';
import { analyticsService } from '../../services/analyticsService';
import { reportsService } from '../../services/reportsService';
import { marksService } from '../../services/marksService';

export function StudentDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [studentProfile, setStudentProfile] = useState(null);
  const [studentAnalytics, setStudentAnalytics] = useState(null);
  const [myMarks, setMyMarks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchStudentData = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    // 1. Fetch Profile
    try {
      const profile = await studentService.getMyStudentProfile();
      setStudentProfile(profile);
    } catch (err) {
      if (err.status === 404) {
        setErrorMessage('No student academic record is linked to your email address yet.');
      } else {
        setErrorMessage(err.message || 'Unable to load your student profile.');
      }
    }

    // 2. Fetch Live Personal Analytics & Marks
    try {
      const [analyticsData, marksRes] = await Promise.all([
        analyticsService.getStudentAnalytics(),
        marksService.getMyMarks({ limit: 5 }),
      ]);
      setStudentAnalytics(analyticsData);
      setMyMarks(marksRes?.items || []);
    } catch (err) {
      // Graceful fallback if no records yet
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentData();
  }, []);

  const handleDownloadPdf = async () => {
    const sId = studentAnalytics?.student_id || studentProfile?.student_id;
    if (!sId) return;
    setIsDownloadingPdf(true);
    try {
      await reportsService.exportStudentPdf(sId);
    } catch (err) {
      alert(`PDF download failed: ${err.message}`);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const todayClasses = [
    { code: 'CS-301', title: 'Design & Analysis of Algorithms', time: '10:00 AM - 11:30 AM', room: 'LH-302', faculty: 'Prof. Marcus Vance' },
    { code: 'CS-302', title: 'Database Management Systems', time: '11:30 AM - 01:00 PM', room: 'LH-105', faculty: 'Dr. Anita Desai' },
    { code: 'CS-305', title: 'AI & Machine Learning Lab', time: '02:00 PM - 04:00 PM', room: 'AI-Lab 2', faculty: 'Dr. Robert Chen' }
  ];

  const formatExamType = (type) => {
    const map = {
      internal_1: 'Internal 1',
      internal_2: 'Internal 2',
      model: 'Model Exam',
      semester: 'Semester Exam',
      assignment: 'Assignment',
    };
    return map[type] || type;
  };

  const displayName = studentProfile?.full_name || user?.name || user?.full_name || 'Student';
  const displayDept = studentProfile?.department || user?.department || 'Computer Science & Engineering';
  const displayRoll = studentProfile?.roll_number || studentProfile?.student_id || user?.rollNo || 'Pending Enrollment';
  const displayYear = studentProfile?.year ? `Year ${studentProfile.year}` : user?.semester || 'Year 3';
  const displaySection = studentProfile?.section ? ` • Section ${studentProfile.section}` : '';

  const attSummary = studentAnalytics?.attendance_summary;
  const attendanceValue = attSummary ? `${attSummary.attendance_percentage}%` : '0.0%';
  const attendancePeriod = attSummary && attSummary.total_days > 0
    ? `${attSummary.present_days}/${attSummary.total_days} Days Present`
    : 'No attendance logs';

  const mSummary = studentAnalytics?.marks_summary;
  const overallPercentageValue = mSummary && mSummary.total_subjects > 0
    ? `${mSummary.overall_percentage}%`
    : '0.0%';
  const overallPerformancePeriod = mSummary && mSummary.total_subjects > 0
    ? `${mSummary.passed_subjects}/${mSummary.total_subjects} Passed`
    : 'No evaluations yet';

  const riskLevel = studentAnalytics?.risk_level || 'LOW';

  return (
    <div className="space-y-6">
      {/* Student Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-primary via-[#003da8] to-[#002670] text-white p-6 sm:p-8 rounded-2xl shadow-soft">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white border border-white/20 mb-3">
            <GraduationCap className="w-3.5 h-3.5 text-tertiary-fixed" />
            Student Academic Portal
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {displayName}
          </h1>
          <p className="text-xs sm:text-sm text-blue-100 mt-1.5 max-w-xl">
            {displayDept} • {displayYear}{displaySection} • Roll No: {displayRoll}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="white"
            size="md"
            icon={Bot}
            onClick={() => navigate('/student-portal/ai')}
          >
            Ask EduAI Tutor
          </Button>
          {(studentAnalytics?.student_id || studentProfile?.student_id) && (
            <Button
              variant="outline"
              size="md"
              className="bg-white/10 hover:bg-white/20 text-white border-white/30"
              icon={Download}
              onClick={handleDownloadPdf}
              disabled={isDownloadingPdf}
            >
              {isDownloadingPdf ? 'Generating...' : 'Download PDF'}
            </Button>
          )}
        </div>
      </div>

      {/* Loading Notice */}
      {isLoading && (
        <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-xs flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <Loader2 className="w-4 h-4 text-primary animate-spin" />
          <span>Synchronizing student profile & personal academic records from database...</span>
        </div>
      )}

      {/* Error / Notice Banner */}
      {errorMessage && !isLoading && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between gap-3 text-amber-900 text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <span className="text-[11px] font-semibold text-amber-700">Contact Academic Admin</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="Overall Score"
          value={overallPercentageValue}
          change={mSummary && mSummary.overall_percentage >= 75 ? 'Distinction' : 'Academic Standing'}
          trend="up"
          period={overallPerformancePeriod}
          icon={Award}
          color="primary"
        />
        <StatCard
          title="Overall Attendance"
          value={attendanceValue}
          change={attSummary && attSummary.attendance_percentage < 75 ? 'Low Attendance' : 'Safe Zone'}
          trend={attSummary && attSummary.attendance_percentage < 75 ? 'alert' : 'up'}
          period={attendancePeriod}
          icon={CalendarCheck}
          color="tertiary"
        />
        <StatCard
          title="AI Academic Status"
          value={riskLevel}
          change={studentAnalytics ? `Risk Score: ${studentAnalytics.risk_score}` : 'Evaluated'}
          trend={riskLevel === 'LOW' ? 'up' : 'alert'}
          period="Diagnostic Radar"
          icon={Sparkles}
          color={riskLevel === 'LOW' ? 'secondary' : 'error'}
        />
        <StatCard
          title="Passed Assessments"
          value={mSummary ? `${mSummary.passed_subjects} / ${mSummary.total_subjects}` : '0 / 0'}
          change="Curriculum Modules"
          trend="up"
          period={displayYear}
          icon={BookOpen}
          color="primary"
        />
      </div>

      {/* Main Grid: Today's Classes & Recent Grades */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Schedule & AI Insights */}
        <div className="lg:col-span-8 space-y-6">
          <Card
            title="Today's Timetable & Lectures"
            subtitle="Scheduled lectures for today"
            headerAction={<Badge variant="primary" size="sm">3 Classes Today</Badge>}
          >
            <div className="space-y-3">
              {todayClasses.map((cls, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-surface-container-low/70 border border-outline-variant/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs px-2 py-0.5 rounded bg-primary-container text-white">
                        {cls.code}
                      </span>
                      <h4 className="font-bold text-sm text-on-surface">{cls.title}</h4>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1">Faculty: {cls.faculty}</p>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-on-surface-variant">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-primary" />
                      {cls.time}
                    </span>
                    <span className="flex items-center gap-1 font-semibold text-tertiary">
                      <MapPin className="w-3.5 h-3.5" />
                      {cls.room}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* AI Insights & Personalized Study Plan */}
          {studentAnalytics && (
            <Card title="Personalized Academic Insights & Guidance" subtitle="Generated by EduManage Academic Risk Radar">
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-surface-container-low/80 border border-outline-variant/40 space-y-2">
                  <h5 className="font-bold text-xs text-on-surface flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-primary" />
                    Key Diagnostic Factors
                  </h5>
                  <ul className="space-y-1 text-xs text-on-surface-variant">
                    {studentAnalytics.risk_factors.map((factor, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-3.5 rounded-xl bg-primary/5 border border-primary/20 space-y-2">
                  <h5 className="font-bold text-xs text-primary flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-tertiary" />
                    Actionable Recommendations
                  </h5>
                  <ul className="space-y-1 text-xs text-on-surface">
                    {studentAnalytics.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-tertiary mt-0.5">✓</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Right 4 Cols: Recent Grades & AI Tutor Card */}
        <div className="lg:col-span-4 space-y-6">
          {/* EduAI Assistant Promo Card */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-900 via-blue-900 to-[#1e1b4b] text-white shadow-soft">
            <div className="flex items-center gap-2 text-xs font-bold uppercase text-tertiary-fixed">
              <Bot className="w-4 h-4" />
              <span>EduAI Academic Tutor</span>
            </div>
            <h3 className="font-display text-lg font-bold mt-2">Need help with coursework?</h3>
            <p className="text-xs text-blue-200 mt-1 leading-relaxed">
              Ask questions on algorithm proofs, SQL queries, or request interactive practice problems.
            </p>
            <Button
              variant="container"
              size="sm"
              className="mt-4 bg-tertiary-fixed text-[#002113] hover:bg-emerald-300 font-bold w-full"
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => navigate('/student-portal/ai')}
            >
              Open AI Chatbot
            </Button>
          </div>

          {/* Recent Grades */}
          <Card title="Recent Assessment Scores" subtitle="Real-time evaluation postings from database">
            {myMarks.length === 0 ? (
              <div className="py-6 text-center text-xs text-on-surface-variant space-y-1">
                <p className="font-semibold text-on-surface">No evaluations published yet.</p>
                <p>Assessment scores entered by faculty will appear here automatically.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {myMarks.map((g) => (
                  <div key={g.marks_id || g.id} className="p-3 rounded-xl bg-surface-container-low/70 border border-outline-variant/30 flex items-center justify-between">
                    <div>
                      <h5 className="font-bold text-xs text-on-surface">{g.subject_code}: {g.subject_name}</h5>
                      <p className="text-[11px] text-on-surface-variant mt-0.5">
                        {formatExamType(g.exam_type)} • Sem {g.semester}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-xs text-primary">{g.marks_obtained} / {g.max_marks}</span>
                      <span className={`block text-[10px] font-bold ${
                        g.grade === 'A+' ? 'text-emerald-700' :
                        g.grade === 'A' ? 'text-blue-700' :
                        g.grade === 'B' ? 'text-indigo-700' :
                        g.grade === 'C' ? 'text-amber-700' : 'text-error'
                      }`}>
                        Grade {g.grade} ({g.percentage}%)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default StudentDashboard;

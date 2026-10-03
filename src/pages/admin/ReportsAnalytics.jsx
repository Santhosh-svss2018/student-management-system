import React, { useState, useEffect } from 'react';
import {
  FileBarChart2,
  Download,
  Calendar,
  Filter,
  TrendingUp,
  Award,
  Users,
  CheckCircle2,
  FileSpreadsheet,
  FileText,
  Loader2,
  RefreshCw,
  AlertCircle,
  Search,
  BookOpen
} from 'lucide-react';
import Card, { StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Select from '../../components/common/Select';
import Table, { TableHead, TableBody, TableRow, TableCell } from '../../components/common/Table';
import { analyticsService } from '../../services/analyticsService';
import { reportsService } from '../../services/reportsService';

export function ReportsAnalytics() {
  const [activeTab, setActiveTab] = useState('students'); // 'students' | 'attendance' | 'marks' | 'departments'
  const [selectedDept, setSelectedDept] = useState('All Departments');
  const [selectedYear, setSelectedYear] = useState('All');
  const [selectedSemester, setSelectedSemester] = useState('All Semesters');
  const [searchQuery, setSearchQuery] = useState('');

  const [overview, setOverview] = useState(null);
  const [academicAnalytics, setAcademicAnalytics] = useState(null);
  const [departmentsData, setDepartmentsData] = useState([]);
  const [reportData, setReportData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchReportsData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      // 1. Fetch live institutional analytics
      const [ovData, acadData, deptData] = await Promise.all([
        analyticsService.getAdminOverview(),
        analyticsService.getAdminAcademic(),
        analyticsService.getAdminDepartments(),
      ]);
      setOverview(ovData);
      setAcademicAnalytics(acadData);
      setDepartmentsData(deptData?.departments || []);

      // 2. Fetch specific active tab report data
      const deptFilter = selectedDept === 'All Departments' ? '' : selectedDept;
      const yearFilter = selectedYear === 'All' ? null : parseInt(selectedYear.replace(/\D/g, '')) || null;

      if (activeTab === 'students') {
        const res = await reportsService.getStudentsReport({
          department: deptFilter,
          year: yearFilter,
          search: searchQuery,
          limit: 20,
        });
        setReportData(res || { items: [], total: 0 });
      } else if (activeTab === 'attendance') {
        const res = await reportsService.getAttendanceReport({
          department: deptFilter,
          year: yearFilter,
          limit: 20,
        });
        setReportData(res || { items: [], total: 0 });
      } else if (activeTab === 'marks') {
        const semNum = selectedSemester === 'All Semesters' ? null : parseInt(selectedSemester.replace(/\D/g, '')) || null;
        const res = await reportsService.getMarksReport({
          department: deptFilter,
          semester: semNum,
          limit: 20,
        });
        setReportData(res || { items: [], total: 0 });
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to fetch live institutional report data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsData();
  }, [activeTab, selectedDept, selectedYear, selectedSemester]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchReportsData();
  };

  const handleExportCsv = async () => {
    setIsExporting(true);
    try {
      const deptFilter = selectedDept === 'All Departments' ? '' : selectedDept;
      const yearFilter = selectedYear === 'All' ? null : parseInt(selectedYear.replace(/\D/g, '')) || null;
      const semNum = selectedSemester === 'All Semesters' ? null : parseInt(selectedSemester.replace(/\D/g, '')) || null;

      if (activeTab === 'students' || activeTab === 'departments') {
        await reportsService.exportStudentsCsv({ department: deptFilter, year: yearFilter });
      } else if (activeTab === 'attendance') {
        await reportsService.exportAttendanceCsv({ department: deptFilter, year: yearFilter });
      } else if (activeTab === 'marks') {
        await reportsService.exportMarksCsv({ department: deptFilter, semester: semNum });
      }
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadStudentPdf = async (studentId) => {
    if (!studentId) return;
    try {
      await reportsService.exportStudentPdf(studentId);
    } catch (err) {
      alert(`PDF Export failed: ${err.message}`);
    }
  };

  const gradeDistribution = academicAnalytics?.grade_distribution || overview?.grade_distribution || {};
  const totalEvaluations = academicAnalytics?.total_marks_evaluated || overview?.total_marks_records || 0;

  return (
    <div className="space-y-6">
      {/* Page Header with Export Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface flex items-center gap-2.5">
            <FileBarChart2 className="w-6 h-6 text-primary" />
            Institutional Reports & Analytics
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Real-time academic performance indicators, grade spreads, and exportable datasets.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={FileSpreadsheet}
            onClick={handleExportCsv}
            disabled={isExporting}
          >
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </Button>
          <Button
            variant="container"
            size="sm"
            icon={Download}
            onClick={() => {
              if (reportData.items && reportData.items.length > 0) {
                handleDownloadStudentPdf(reportData.items[0].student_id);
              } else {
                handleExportCsv();
              }
            }}
          >
            Download PDF Report
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft flex flex-wrap items-center gap-4">
        <div className="flex-1 min-w-[180px]">
          <Select
            label="Academic Department"
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            options={['All Departments', ...departmentsData.map((d) => d.department)]}
          />
        </div>
        <div className="flex-1 min-w-[150px]">
          <Select
            label="Year Level"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            options={['All', 'Year 1', 'Year 2', 'Year 3', 'Year 4']}
          />
        </div>
        <div className="flex-1 min-w-[150px]">
          <Select
            label="Semester"
            value={selectedSemester}
            onChange={(e) => setSelectedSemester(e.target.value)}
            options={['All Semesters', 'Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8']}
          />
        </div>
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 min-w-[200px]">
          <input
            type="text"
            placeholder="Search student or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-low text-on-surface focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <Button variant="outline" size="sm" icon={Search} type="submit">
            Search
          </Button>
        </form>
      </div>

      {/* Loading Notice */}
      {isLoading && (
        <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-xs flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <Loader2 className="w-4 h-4 text-primary animate-spin" />
          <span>Generating real-time institutional report from MongoDB records...</span>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && !isLoading && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={fetchReportsData}>
            Retry
          </Button>
        </div>
      )}

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Students Enrolled"
          value={overview ? overview.active_students.toLocaleString() : '0'}
          change={`${overview ? overview.total_students : 0} Total Records`}
          trend="up"
          period="Active database cohort"
          icon={Users}
          color="primary"
        />
        <StatCard
          title="Overall Attendance Rate"
          value={overview ? `${overview.overall_attendance_percentage}%` : '0.0%'}
          change="Real-time logs"
          trend="up"
          period="All tracked sessions"
          icon={TrendingUp}
          color="tertiary"
        />
        <StatCard
          title="Curriculum Pass Rate"
          value={academicAnalytics ? `${academicAnalytics.pass_percentage}%` : '0.0%'}
          change={`${totalEvaluations} Assessments`}
          trend="up"
          period="Pass score >= 40%"
          icon={CheckCircle2}
          color="secondary"
        />
        <StatCard
          title="Academic Mean Score"
          value={academicAnalytics ? `${academicAnalytics.average_percentage}%` : '0.0%'}
          change={academicAnalytics?.highest_performing_subject ? `Top: ${academicAnalytics.highest_performing_subject}` : 'Institution avg'}
          trend="up"
          period="Out of 100%"
          icon={Award}
          color="primary"
        />
      </div>

      {/* Grade Distribution & Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <Card
            title="University Grade Spread Distribution"
            subtitle="Consolidated real evaluations across all departments"
          >
            <div className="space-y-3.5 mt-2">
              {Object.keys(gradeDistribution).length === 0 ? (
                <div className="py-6 text-center text-xs text-on-surface-variant">
                  No evaluation grades published yet.
                </div>
              ) : (
                Object.entries(gradeDistribution).map(([grade, count]) => {
                  const pct = totalEvaluations > 0 ? Math.round((count / totalEvaluations) * 100) : 0;
                  const colorMap = {
                    'A+': 'bg-emerald-500',
                    'A': 'bg-blue-600',
                    'B': 'bg-indigo-500',
                    'C': 'bg-amber-500',
                    'D': 'bg-orange-500',
                    'E': 'bg-rose-400',
                    'F': 'bg-red-500',
                  };
                  return (
                    <div key={grade} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-on-surface">Grade {grade}</span>
                        <span className="text-on-surface-variant font-medium">
                          {count} Evaluations ({pct}%)
                        </span>
                      </div>
                      <div className="w-full h-3 bg-surface-container rounded-full overflow-hidden">
                        <div
                          className={`h-full ${colorMap[grade] || 'bg-primary'} rounded-full transition-all duration-500`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-6">
          <Card
            title="Departmental Performance Overview"
            subtitle="Live breakdown by academic department"
          >
            <div className="space-y-3 mt-1 text-xs">
              {departmentsData.length === 0 ? (
                <div className="py-6 text-center text-xs text-on-surface-variant">
                  No departments recorded yet.
                </div>
              ) : (
                departmentsData.map((d, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-surface-container-low/60 border border-outline-variant/40 flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-on-surface">{d.department}</h4>
                      <p className="text-on-surface-variant mt-0.5">
                        {d.student_count} Students • Attendance: {d.attendance_percentage}%
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-primary text-sm">{d.academic_percentage}%</span>
                      <span className="block text-[10px] text-on-surface-variant">Avg Academic</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Tab Navigation for Detailed Data Tables */}
      <div className="border-b border-outline-variant">
        <nav className="flex space-x-6 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('students')}
            className={`pb-3 transition-colors ${
              activeTab === 'students'
                ? 'border-b-2 border-primary text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Students Report ({activeTab === 'students' ? reportData.total : overview?.active_students || 0})
          </button>
          <button
            onClick={() => setActiveTab('attendance')}
            className={`pb-3 transition-colors ${
              activeTab === 'attendance'
                ? 'border-b-2 border-primary text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Attendance Logs ({overview?.total_attendance_records || 0})
          </button>
          <button
            onClick={() => setActiveTab('marks')}
            className={`pb-3 transition-colors ${
              activeTab === 'marks'
                ? 'border-b-2 border-primary text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Marks & Evaluations ({totalEvaluations})
          </button>
          <button
            onClick={() => setActiveTab('departments')}
            className={`pb-3 transition-colors ${
              activeTab === 'departments'
                ? 'border-b-2 border-primary text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Department Matrix ({departmentsData.length})
          </button>
        </nav>
      </div>

      {/* Dynamic Report Table View */}
      <Card
        title={
          activeTab === 'students' ? 'Student Demographic & Performance Roster' :
          activeTab === 'attendance' ? 'Session Attendance Records' :
          activeTab === 'marks' ? 'Consolidated Assessment Grades' : 'Departmental Matrix'
        }
        subtitle="Real database records matching active filters"
      >
        {activeTab === 'students' && (
          <Table>
            <TableHead>
              <TableRow hoverable={false}>
                <TableCell as="th">Student ID</TableCell>
                <TableCell as="th">Student Name</TableCell>
                <TableCell as="th">Department</TableCell>
                <TableCell as="th">Year / Sec</TableCell>
                <TableCell as="th">Attendance</TableCell>
                <TableCell as="th">Academic Avg</TableCell>
                <TableCell as="th">Risk</TableCell>
                <TableCell as="th" align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reportData.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-6 text-xs text-on-surface-variant">
                    No student records match the selected filter criteria.
                  </TableCell>
                </TableRow>
              ) : (
                reportData.items.map((s) => (
                  <TableRow key={s.student_id}>
                    <TableCell className="font-mono text-xs font-bold text-primary">{s.student_id}</TableCell>
                    <TableCell className="font-semibold text-on-surface">{s.full_name}</TableCell>
                    <TableCell>{s.department}</TableCell>
                    <TableCell>Year {s.year} - {s.section}</TableCell>
                    <TableCell>{s.attendance_percentage}%</TableCell>
                    <TableCell className="font-bold text-on-surface">{s.academic_percentage}%</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          s.risk_level === 'LOW' ? 'success' :
                          s.risk_level === 'MEDIUM' ? 'warning' : 'error'
                        }
                        size="sm"
                      >
                        {s.risk_level}
                      </Badge>
                    </TableCell>
                    <TableCell align="right">
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={Download}
                        onClick={() => handleDownloadStudentPdf(s.student_id)}
                      >
                        PDF
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}

        {activeTab === 'attendance' && (
          <Table>
            <TableHead>
              <TableRow hoverable={false}>
                <TableCell as="th">Attendance ID</TableCell>
                <TableCell as="th">Student</TableCell>
                <TableCell as="th">Department</TableCell>
                <TableCell as="th">Date</TableCell>
                <TableCell as="th">Status</TableCell>
                <TableCell as="th">Marked By</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reportData.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-6 text-xs text-on-surface-variant">
                    No attendance records found.
                  </TableCell>
                </TableRow>
              ) : (
                reportData.items.map((a) => (
                  <TableRow key={a.attendance_id}>
                    <TableCell className="font-mono text-xs text-primary">{a.attendance_id}</TableCell>
                    <TableCell className="font-semibold text-on-surface">{a.student_name} ({a.student_id})</TableCell>
                    <TableCell>{a.department}</TableCell>
                    <TableCell>{a.date}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          a.status === 'present' ? 'success' :
                          a.status === 'absent' ? 'error' : 'warning'
                        }
                        size="sm"
                      >
                        {a.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{a.marked_by}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}

        {activeTab === 'marks' && (
          <Table>
            <TableHead>
              <TableRow hoverable={false}>
                <TableCell as="th">Marks ID</TableCell>
                <TableCell as="th">Student</TableCell>
                <TableCell as="th">Subject</TableCell>
                <TableCell as="th">Sem</TableCell>
                <TableCell as="th">Exam</TableCell>
                <TableCell as="th">Score</TableCell>
                <TableCell as="th">Grade</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reportData.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-6 text-xs text-on-surface-variant">
                    No marks records found.
                  </TableCell>
                </TableRow>
              ) : (
                reportData.items.map((m) => (
                  <TableRow key={m.marks_id}>
                    <TableCell className="font-mono text-xs text-primary">{m.marks_id}</TableCell>
                    <TableCell className="font-semibold text-on-surface">{m.student_name}</TableCell>
                    <TableCell>{m.subject_code}: {m.subject_name}</TableCell>
                    <TableCell>Sem {m.semester}</TableCell>
                    <TableCell>{m.exam_type}</TableCell>
                    <TableCell className="font-bold text-on-surface">{m.marks_obtained} / {m.max_marks} ({m.percentage}%)</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          m.grade === 'A+' ? 'success' :
                          m.grade === 'A' ? 'primary' :
                          m.grade === 'B' ? 'secondary' :
                          m.grade === 'C' ? 'warning' : 'error'
                        }
                        size="sm"
                      >
                        {m.grade}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}

        {activeTab === 'departments' && (
          <Table>
            <TableHead>
              <TableRow hoverable={false}>
                <TableCell as="th">Department</TableCell>
                <TableCell as="th">Enrolled</TableCell>
                <TableCell as="th">Attendance</TableCell>
                <TableCell as="th">Academic Avg</TableCell>
                <TableCell as="th">At-Risk Alerts</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {departmentsData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-6 text-xs text-on-surface-variant">
                    No department data available.
                  </TableCell>
                </TableRow>
              ) : (
                departmentsData.map((d, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-semibold text-on-surface">{d.department}</TableCell>
                    <TableCell>{d.student_count}</TableCell>
                    <TableCell>{d.attendance_percentage}%</TableCell>
                    <TableCell className="font-bold text-primary">{d.academic_percentage}%</TableCell>
                    <TableCell>
                      <Badge variant={d.at_risk_count > 0 ? 'warning' : 'success'} size="sm">
                        {d.at_risk_count} Flagged
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}

export default ReportsAnalytics;

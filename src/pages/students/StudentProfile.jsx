import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Mail,
  Phone,
  MapPin,
  CalendarCheck,
  Award,
  BookOpen,
  ArrowLeft,
  Edit,
  Download,
  CheckCircle2,
  Users,
  ShieldCheck,
  Clock,
  Loader2,
  AlertCircle,
  Key
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Tabs from '../../components/common/Tabs';
import Table, { TableHead, TableBody, TableRow, TableCell } from '../../components/common/Table';
import ChangePasswordModal from '../../components/common/ChangePasswordModal';
import { useAuth } from '../../context/AuthContext';
import { studentService } from '../../services/studentService';
import { attendanceService } from '../../services/attendanceService';
import { marksService } from '../../services/marksService';
import { reportsService } from '../../services/reportsService';
import { MOCK_COURSES } from '../../data/mockData';

export function StudentProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  const [student, setStudent] = useState(null);
  const [attendanceSummary, setAttendanceSummary] = useState(null);
  const [marksSummary, setMarksSummary] = useState(null);
  const [studentMarks, setStudentMarks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('academic');

  useEffect(() => {
    let isMounted = true;

    async function loadStudentData() {
      if (!id) {
        setIsLoading(false);
        setErrorMessage('No student identifier provided in URL.');
        return;
      }

      setIsLoading(true);
      setErrorMessage(null);

      try {
        const data = await studentService.getStudent(id);
        if (isMounted) {
          setStudent(data);
        }

        const canonicalId = data?.student_id || id;

        // Fetch real attendance summary for student
        try {
          const summary = await attendanceService.getStudentAttendanceSummary(canonicalId);
          if (isMounted) {
            setAttendanceSummary(summary);
          }
        } catch (summaryErr) {
          // Fallback if not seeded yet
        }

        // Fetch real marks records & summary for student
        try {
          const [marksRes, mSummary] = await Promise.all([
            marksService.getStudentMarks(canonicalId, { limit: 20 }),
            marksService.getStudentMarksSummary(canonicalId),
          ]);
          if (isMounted) {
            setStudentMarks(marksRes?.items || []);
            setMarksSummary(mSummary);
          }
        } catch (marksErr) {
          // Fallback if not seeded yet
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage(err.message || `Unable to load student with ID "${id}".`);
          setStudent(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadStudentData();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const tabs = [
    { id: 'academic', label: 'Academic Performance', icon: Award },
    { id: 'attendance', label: 'Attendance Breakdown', icon: CalendarCheck },
    { id: 'courses', label: 'Enrolled Courses', icon: BookOpen, count: 5 },
    { id: 'guardian', label: 'Personal & Contact', icon: Users },
  ];

  const formatExamType = (type) => {
    const map = {
      internal_1: 'Internal 1',
      internal_2: 'Internal 2',
      model: 'Model Exam',
      semester: 'Semester Final',
      assignment: 'Assignment',
    };
    return map[type] || type;
  };

  const getGradeBadge = (grade) => {
    const styles = {
      'A+': 'bg-emerald-100 text-emerald-800 border-emerald-300',
      'A': 'bg-blue-100 text-blue-800 border-blue-300',
      'B': 'bg-indigo-100 text-indigo-800 border-indigo-300',
      'C': 'bg-amber-100 text-amber-800 border-amber-300',
      'D': 'bg-orange-100 text-orange-800 border-orange-300',
      'E': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'F': 'bg-red-100 text-red-800 border-red-300',
    };
    return (
      <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold border ${styles[grade] || 'bg-slate-100 text-slate-800'}`}>
        {grade}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-3">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <p className="text-xs font-semibold text-on-surface-variant">Loading student profile...</p>
      </div>
    );
  }

  if (errorMessage || !student) {
    return (
      <div className="space-y-6 max-w-3xl mx-auto py-8">
        <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => navigate('/students')}>
          Back to Directory
        </Button>
        <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-error mx-auto" />
          <h3 className="font-display font-bold text-lg text-on-surface">Student Record Not Found</h3>
          <p className="text-xs sm:text-sm text-red-700 max-w-md mx-auto">
            {errorMessage || `The student identifier "${id}" could not be retrieved from the database.`}
          </p>
          <div className="pt-2">
            <Button variant="container" size="sm" onClick={() => navigate('/students')}>
              Return to Student Directory
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const studentName = student.full_name || student.name || 'Student';
  const studentRoll = student.roll_number || student.rollNo || student.student_id;
  const targetId = student.student_id || student.id;
  const isActive = student.is_active !== false;
  const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(studentName)}&backgroundColor=004494,0066cc,2563eb`;

  const attendanceValue = attendanceSummary ? `${attendanceSummary.attendance_percentage}%` : '94.2%';
  const overallMarksValue = marksSummary && marksSummary.total_subjects > 0
    ? `${marksSummary.overall_percentage}%`
    : '8.84';

  const handleDownloadTranscript = async () => {
    if (!targetId) return;
    setIsExportingPdf(true);
    try {
      await reportsService.exportStudentPdf(targetId);
    } catch (err) {
      alert(err.message || 'Failed to download student transcript PDF.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Back Bar */}
      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => navigate('/students')}>
          Back to Directory
        </Button>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={handleDownloadTranscript}
            disabled={isExportingPdf}
          >
            {isExportingPdf ? 'Exporting PDF...' : 'Download Transcript'}
          </Button>
          {/* Admin-only Password Management */}
          {isAdmin && (
            <Button
              variant="outline"
              size="sm"
              icon={Key}
              onClick={() => setIsPasswordModalOpen(true)}
            >
              Change Password
            </Button>
          )}
          {/* Edit Button: Admin only */}
          {isAdmin && (
            <Button
              variant="container"
              size="sm"
              icon={Edit}
              onClick={() => navigate(`/students/${targetId}/edit`)}
            >
              Edit Record
            </Button>
          )}
        </div>
      </div>

      {/* Student Profile Hero Header */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 sm:p-8 shadow-soft flex flex-col md:flex-row items-start md:items-center gap-6">
        <img
          src={avatarUrl}
          alt={studentName}
          className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl object-cover ring-4 ring-primary/20 shadow-card bg-primary/10"
        />

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-on-surface">
              {studentName}
            </h1>
            <Badge variant="primary" size="md">Roll: {studentRoll}</Badge>
            <Badge variant="status" size="md" dot>{isActive ? 'Active' : 'Inactive'}</Badge>
          </div>

          <p className="text-sm font-semibold text-primary">
            {student.department} • Year {student.year || 1} {student.section ? `(${student.section})` : ''}
          </p>

          <div className="flex flex-wrap items-center gap-4 sm:gap-6 mt-4 text-xs text-on-surface-variant">
            <div className="flex items-center gap-1.5">
              <Mail className="w-4 h-4 text-on-surface-variant" />
              <span>{student.email}</span>
            </div>
            {student.phone && (
              <div className="flex items-center gap-1.5">
                <Phone className="w-4 h-4 text-on-surface-variant" />
                <span>{student.phone}</span>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-on-surface-variant" />
              <span>Student ID: {student.student_id}</span>
            </div>
          </div>
        </div>

        {/* Highlight Score & Attendance Pill */}
        <div className="flex sm:flex-col gap-3 w-full sm:w-auto">
          <div className="flex-1 p-3.5 bg-blue-50/70 border border-blue-200 rounded-xl text-center min-w-[120px]">
            <p className="text-[10px] font-bold uppercase text-blue-900">
              {marksSummary && marksSummary.total_subjects > 0 ? 'Overall Score' : 'Current CGPA'}
            </p>
            <p className="font-display text-2xl font-bold text-primary mt-0.5">{overallMarksValue}</p>
          </div>
          <div className="flex-1 p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl text-center min-w-[120px]">
            <p className="text-[10px] font-bold uppercase text-emerald-900">Attendance</p>
            <p className="font-display text-2xl font-bold text-tertiary mt-0.5">{attendanceValue}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab 1: Academic Performance */}
      {activeTab === 'academic' && (
        <div className="space-y-6">
          {marksSummary && marksSummary.total_subjects > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 bg-surface-container-low rounded-xl">
                <p className="text-[10px] uppercase font-bold text-on-surface-variant">Evaluated Courses</p>
                <p className="font-bold text-lg text-on-surface mt-1">{marksSummary.total_subjects}</p>
              </div>
              <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-emerald-800">Passed Assessments</p>
                <p className="font-bold text-lg text-emerald-700 mt-1">{marksSummary.passed_subjects}</p>
              </div>
              <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-blue-800">Total Marks Scored</p>
                <p className="font-bold text-lg text-primary mt-1">{marksSummary.total_marks_obtained} / {marksSummary.total_max_marks}</p>
              </div>
              <div className="p-3.5 bg-indigo-50 border border-indigo-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-indigo-800">Overall Percentage</p>
                <p className="font-bold text-lg text-indigo-700 mt-1">{marksSummary.overall_percentage}%</p>
              </div>
            </div>
          )}

          <Card title="Assessment Scores & Evaluations" subtitle="Real-time evaluation records retrieved from MongoDB">
            {studentMarks.length === 0 ? (
              <div className="py-8 text-center text-xs text-on-surface-variant space-y-1">
                <Award className="w-8 h-8 text-on-surface-variant/40 mx-auto mb-2" />
                <p className="font-semibold text-on-surface">No evaluation marks recorded yet.</p>
                <p>Assessment scores entered by faculty will be displayed here.</p>
              </div>
            ) : (
              <Table>
                <TableHead>
                  <TableRow hoverable={false}>
                    <TableCell as="th">Subject / Course</TableCell>
                    <TableCell as="th" className="text-center">Semester</TableCell>
                    <TableCell as="th">Assessment</TableCell>
                    <TableCell as="th" className="text-center">Score</TableCell>
                    <TableCell as="th" className="text-center">Percentage</TableCell>
                    <TableCell as="th" className="text-center">Grade</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {studentMarks.map((m) => (
                    <TableRow key={m.marks_id || m.id}>
                      <TableCell>
                        <div className="font-semibold text-xs text-on-surface">{m.subject_code}</div>
                        <div className="text-[11px] text-on-surface-variant">{m.subject_name}</div>
                      </TableCell>
                      <TableCell className="text-center text-xs font-semibold text-on-surface">
                        Sem {m.semester}
                      </TableCell>
                      <TableCell>
                        <Badge variant="primary" size="sm">
                          {formatExamType(m.exam_type)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center font-bold text-xs text-on-surface">
                        {m.marks_obtained} / {m.max_marks}
                      </TableCell>
                      <TableCell className="text-center font-bold text-xs text-primary">
                        {m.percentage}%
                      </TableCell>
                      <TableCell className="text-center">
                        {getGradeBadge(m.grade)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>
        </div>
      )}

      {/* Tab 2: Attendance Breakdown */}
      {activeTab === 'attendance' && (
        <div className="space-y-6">
          {attendanceSummary && (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="p-3 bg-surface-container-low rounded-xl">
                <p className="text-[10px] uppercase font-bold text-on-surface-variant">Total Sessions</p>
                <p className="font-bold text-lg text-on-surface mt-1">{attendanceSummary.total_days}</p>
              </div>
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-emerald-800">Present</p>
                <p className="font-bold text-lg text-emerald-700 mt-1">{attendanceSummary.present_days}</p>
              </div>
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-red-800">Absent</p>
                <p className="font-bold text-lg text-error mt-1">{attendanceSummary.absent_days}</p>
              </div>
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-amber-800">Late</p>
                <p className="font-bold text-lg text-amber-700 mt-1">{attendanceSummary.late_days}</p>
              </div>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-[10px] uppercase font-bold text-blue-800">Excused</p>
                <p className="font-bold text-lg text-primary mt-1">{attendanceSummary.excused_days}</p>
              </div>
            </div>
          )}

          <Card title="Course-Wise Attendance Breakdown" subtitle="Minimum mandatory requirement: 75% attendance">
            <div className="space-y-4">
              {MOCK_COURSES.map((course) => (
                <div key={course.id} className="p-3.5 bg-surface-container-low rounded-xl">
                  <div className="flex justify-between items-center mb-1.5 text-xs">
                    <span className="font-bold text-on-surface">{course.code}: {course.title}</span>
                    <span className="font-bold text-tertiary">{course.attendance}%</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-600 rounded-full"
                      style={{ width: `${course.attendance}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Tab 3: Courses */}
      {activeTab === 'courses' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MOCK_COURSES.map((course) => (
            <Card key={course.id} title={`${course.code}: ${course.title}`} subtitle={`Instructor: ${course.instructor}`}>
              <div className="text-xs space-y-2 text-on-surface-variant">
                <div className="flex justify-between">
                  <span>Credits</span>
                  <span className="font-semibold text-on-surface">{course.credits} Credits</span>
                </div>
                <div className="flex justify-between">
                  <span>Lecture Timetable</span>
                  <span className="font-semibold text-on-surface">{course.schedule}</span>
                </div>
                <div className="flex justify-between">
                  <span>Room / Lab</span>
                  <span className="font-semibold text-on-surface">{course.room}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Tab 4: Guardian & Personal */}
      {activeTab === 'guardian' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Demographic & Identity Records">
            <div className="space-y-3 text-xs sm:text-sm">
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Student ID</span>
                <span className="font-semibold text-on-surface font-mono">{student.student_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Roll Number</span>
                <span className="font-semibold text-on-surface font-mono">{student.roll_number}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Date of Birth</span>
                <span className="font-semibold text-on-surface">{student.date_of_birth || 'Not recorded'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Gender</span>
                <span className="font-semibold text-on-surface">{student.gender || 'Not specified'}</span>
              </div>
              <div className="py-1">
                <span className="text-on-surface-variant block mb-1">Residential Address</span>
                <span className="font-semibold text-on-surface leading-relaxed">
                  {student.address || 'No residential address on file'}
                </span>
              </div>
            </div>
          </Card>

          <Card title="Department & Program Enrollment">
            <div className="space-y-3 text-xs sm:text-sm">
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Major / Department</span>
                <span className="font-semibold text-on-surface">{student.department}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Academic Year</span>
                <span className="font-semibold text-on-surface">Year {student.year}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Assigned Section</span>
                <span className="font-semibold text-on-surface">{student.section || 'Unassigned'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline-variant/30">
                <span className="text-on-surface-variant">Enrollment Status</span>
                <Badge variant="status" size="sm" dot>{isActive ? 'Active' : 'Inactive'}</Badge>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-on-surface-variant">Registered Date</span>
                <span className="font-semibold text-on-surface">
                  {student.created_at ? new Date(student.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Admin Password Management Dialog */}
      {isAdmin && (
        <ChangePasswordModal
          isOpen={isPasswordModalOpen}
          onClose={() => setIsPasswordModalOpen(false)}
          targetUser={student}
        />
      )}
    </div>
  );
}

export default StudentProfile;

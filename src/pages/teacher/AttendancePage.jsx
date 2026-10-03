import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  CalendarCheck,
  CheckCircle2,
  XCircle,
  Clock,
  Save,
  Users,
  Calendar,
  Filter,
  Download,
  QrCode,
  Check,
  AlertCircle,
  Loader2,
  Trash2,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Select from '../../components/common/Select';
import Input from '../../components/common/Input';
import Table, { TableHead, TableBody, TableRow, TableCell } from '../../components/common/Table';
import { useAuth } from '../../context/AuthContext';
import { studentService } from '../../services/studentService';
import { attendanceService } from '../../services/attendanceService';

export function AttendancePage() {
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  // Filters & Session State
  const [selectedCourse, setSelectedCourse] = useState('CS-301');
  const [selectedDept, setSelectedDept] = useState('All');
  const [sessionDate, setSessionDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [statusFilter, setStatusFilter] = useState('All');

  // Data State
  const [students, setStudents] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [attendanceList, setAttendanceList] = useState([]);

  // UI States
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  // Deletion Modal State (Admin only)
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Load students and attendance records for sessionDate
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setApiError(null);

    try {
      // 1. Fetch real students from backend
      const studentRes = await studentService.getStudents(1, 100);
      const studentItems = studentRes?.items || [];
      setStudents(studentItems);

      // 2. Fetch existing attendance records for the selected date
      const attendanceRes = await attendanceService.getAttendance({ date: sessionDate, limit: 100 });
      const records = attendanceRes?.items || [];
      setAttendanceRecords(records);

      // 3. Map students with existing attendance for sessionDate
      const recordMap = new Map();
      records.forEach((rec) => {
        recordMap.set(rec.student_id, rec);
      });

      const initialRoster = studentItems.map((student) => {
        const canonicalId = student.student_id || student.roll_number;
        const existingRecord = recordMap.get(canonicalId) || recordMap.get(student.roll_number);

        const statusRaw = existingRecord ? existingRecord.status : 'present';
        const formattedStatus = statusRaw.charAt(0).toUpperCase() + statusRaw.slice(1).toLowerCase();

        return {
          id: student.id || student.student_id,
          student_id: canonicalId,
          rollNo: student.roll_number || student.student_id,
          name: student.full_name || student.name || 'Student',
          department: student.department || 'Computer Science',
          year: student.year || 1,
          section: student.section || 'A',
          avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(student.full_name || student.name)}&backgroundColor=004494,0066cc,2563eb`,
          status: formattedStatus, // 'Present', 'Absent', 'Late', 'Excused'
          remarks: existingRecord?.remarks || '',
          attendanceId: existingRecord?.attendance_id || null,
          isSaved: Boolean(existingRecord),
        };
      });

      setAttendanceList(initialRoster);
    } catch (err) {
      setApiError(err.message || 'Failed to load attendance records for selected date.');
    } finally {
      setIsLoading(false);
    }
  }, [sessionDate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle status toggle for a student
  const handleStatusChange = (studentId, newStatus) => {
    setAttendanceList((prev) =>
      prev.map((item) => (item.student_id === studentId ? { ...item, status: newStatus } : item))
    );
  };

  // Handle remarks change
  const handleRemarkChange = (studentId, remarks) => {
    setAttendanceList((prev) =>
      prev.map((item) => (item.student_id === studentId ? { ...item, remarks } : item))
    );
  };

  // Mark all students present
  const handleMarkAllPresent = () => {
    setAttendanceList((prev) => prev.map((item) => ({ ...item, status: 'Present' })));
  };

  // Save / Publish attendance
  const handleSaveAttendance = async () => {
    if (attendanceList.length === 0) return;
    setIsSaving(true);
    setFeedback(null);

    let successCount = 0;
    let errorMessages = [];

    try {
      for (const item of attendanceList) {
        const payload = {
          student_id: item.student_id,
          date: sessionDate,
          status: item.status.toLowerCase(),
          remarks: item.remarks?.trim() || null,
        };

        try {
          if (item.attendanceId) {
            // Update existing record
            await attendanceService.updateAttendance(item.attendanceId, {
              status: item.status.toLowerCase(),
              remarks: item.remarks?.trim() || null,
              date: sessionDate,
            });
          } else {
            // Create new record
            await attendanceService.createAttendance(payload);
          }
          successCount++;
        } catch (err) {
          if (err.status === 409) {
            // If already exists on backend, try updating
            try {
              const existingRecord = attendanceRecords.find(
                (r) => r.student_id === item.student_id && r.date === sessionDate
              );
              if (existingRecord) {
                await attendanceService.updateAttendance(existingRecord.attendance_id, {
                  status: item.status.toLowerCase(),
                  remarks: item.remarks?.trim() || null,
                });
                successCount++;
              }
            } catch (innerErr) {
              errorMessages.push(`${item.name}: ${innerErr.message}`);
            }
          } else {
            errorMessages.push(`${item.name}: ${err.message}`);
          }
        }
      }

      if (errorMessages.length === 0) {
        setFeedback({
          type: 'success',
          message: `Attendance for ${sessionDate} successfully saved and synced for ${successCount} students.`,
        });
      } else {
        setFeedback({
          type: 'error',
          message: `Saved ${successCount} records. Issues: ${errorMessages.slice(0, 2).join(', ')}`,
        });
      }

      // Refresh records
      await loadData();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'An unexpected error occurred while saving attendance.',
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Delete attendance record (Admin only)
  const handleConfirmDelete = async () => {
    if (!recordToDelete || !isAdmin) return;
    setIsDeleting(true);

    try {
      await attendanceService.deleteAttendance(recordToDelete.attendanceId);
      setFeedback({
        type: 'success',
        message: `Attendance record for ${recordToDelete.name} on ${sessionDate} was removed.`,
      });
      setRecordToDelete(null);
      await loadData();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to delete attendance record.',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // Filter roster by Department and Status filter
  const displayedRoster = useMemo(() => {
    return attendanceList.filter((item) => {
      const matchDept = selectedDept === 'All' || item.department.toLowerCase().includes(selectedDept.toLowerCase());
      const matchStatus = statusFilter === 'All' || item.status.toLowerCase() === statusFilter.toLowerCase();
      return matchDept && matchStatus;
    });
  }, [attendanceList, selectedDept, statusFilter]);

  // Metrics
  const totalCount = displayedRoster.length;
  const presentCount = displayedRoster.filter((s) => s.status === 'Present').length;
  const absentCount = displayedRoster.filter((s) => s.status === 'Absent').length;
  const lateCount = displayedRoster.filter((s) => s.status === 'Late').length;
  const percentage = totalCount > 0 ? Math.round(((presentCount + lateCount * 0.5) / totalCount) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface flex items-center gap-2.5">
            <CalendarCheck className="w-6 h-6 text-primary" />
            Attendance Management & Daily Marking
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Record, update, and submit student attendance for scheduled classes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={loadData}
            disabled={isLoading || isSaving}
          >
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleMarkAllPresent}
            disabled={isLoading || isSaving || displayedRoster.length === 0}
          >
            Mark All Present
          </Button>
          <Button
            variant="container"
            size="sm"
            icon={isSaving ? Loader2 : Save}
            onClick={handleSaveAttendance}
            disabled={isLoading || isSaving || displayedRoster.length === 0}
          >
            {isSaving ? 'Saving...' : 'Save & Publish'}
          </Button>
        </div>
      </div>

      {/* Feedback Alert Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-xs sm:text-sm animate-in fade-in ${
            feedback.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-tertiary'
              : 'bg-red-50 border-red-200 text-error'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <span className="font-semibold">{feedback.message}</span>
          </div>
          <button
            onClick={() => setFeedback(null)}
            className="p-1 hover:opacity-70 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* API Error Banner */}
      {apiError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between gap-3 text-error text-sm">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Unable to fetch attendance</p>
              <p className="text-xs mt-0.5 text-red-700">{apiError}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={loadData}>
            Retry
          </Button>
        </div>
      )}

      {/* Class & Session Selector Bar */}
      <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Select
          label="Course / Subject"
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
          options={[
            { label: 'CS-301: Design & Analysis of Algorithms', value: 'CS-301' },
            { label: 'CS-402: Cloud Architecture & DevOps', value: 'CS-402' },
            { label: 'CS-305: AI & Machine Learning Lab', value: 'CS-305' }
          ]}
        />
        <Select
          label="Department Filter"
          value={selectedDept}
          onChange={(e) => setSelectedDept(e.target.value)}
          options={[
            { label: 'All Departments', value: 'All' },
            { label: 'Computer Science', value: 'Computer Science' },
            { label: 'Information Technology', value: 'Information Technology' },
            { label: 'Electronics & Communication', value: 'Electronics' },
            { label: 'Mechanical Engineering', value: 'Mechanical' },
            { label: 'Civil Engineering', value: 'Civil' }
          ]}
        />
        <Input
          label="Session Date"
          type="date"
          value={sessionDate}
          onChange={(e) => setSessionDate(e.target.value)}
        />
        <Select
          label="Status Filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { label: 'All Statuses', value: 'All' },
            { label: 'Present', value: 'present' },
            { label: 'Absent', value: 'absent' },
            { label: 'Late', value: 'late' },
            { label: 'Excused', value: 'excused' }
          ]}
        />
      </div>

      {/* Real-time Attendance Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 sm:gap-4">
        <div className="p-3.5 rounded-xl bg-surface-container-lowest border border-outline-variant/50">
          <p className="text-[11px] font-bold text-on-surface-variant uppercase">Total Strength</p>
          <h3 className="font-display text-xl font-bold text-on-surface mt-1">{totalCount} Students</h3>
        </div>
        <div className="p-3.5 rounded-xl bg-emerald-50/80 border border-emerald-200">
          <p className="text-[11px] font-bold text-emerald-800 uppercase">Present</p>
          <h3 className="font-display text-xl font-bold text-emerald-700 mt-1">{presentCount}</h3>
        </div>
        <div className="p-3.5 rounded-xl bg-red-50/80 border border-red-200">
          <p className="text-[11px] font-bold text-red-800 uppercase">Absent</p>
          <h3 className="font-display text-xl font-bold text-error mt-1">{absentCount}</h3>
        </div>
        <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200">
          <p className="text-[11px] font-bold text-amber-800 uppercase">Late / Grace</p>
          <h3 className="font-display text-xl font-bold text-amber-700 mt-1">{lateCount}</h3>
        </div>
        <div className="p-3.5 rounded-xl bg-blue-50/80 border border-blue-200 col-span-2 sm:col-span-1">
          <p className="text-[11px] font-bold text-blue-800 uppercase">Attendance %</p>
          <h3 className="font-display text-xl font-bold text-primary mt-1">{percentage}%</h3>
        </div>
      </div>

      {/* Attendance Roster Table */}
      <Card
        title="Student Class Roster"
        subtitle={`Marking session for ${sessionDate} • ${presentCount} Present / ${absentCount} Absent`}
        padding="none"
      >
        <Table>
          <TableHead>
            <TableRow hoverable={false}>
              <TableCell as="th" className="w-20">Roll No</TableCell>
              <TableCell as="th">Student Name</TableCell>
              <TableCell as="th">Department</TableCell>
              <TableCell as="th" className="text-center">Status Action</TableCell>
              <TableCell as="th">Remarks</TableCell>
              {isAdmin && <TableCell as="th" className="text-right w-16">Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow hoverable={false}>
                <TableCell colSpan={isAdmin ? 6 : 5} className="text-center py-12 text-on-surface-variant">
                  <div className="flex flex-col items-center justify-center gap-3">
                    <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    <p className="text-xs font-semibold">Loading student class roster from server...</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : displayedRoster.length === 0 ? (
              <TableRow hoverable={false}>
                <TableCell colSpan={isAdmin ? 6 : 5} className="text-center py-12 text-on-surface-variant">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Users className="w-10 h-10 text-on-surface-variant/40" />
                    <p className="font-semibold text-sm text-on-surface">No students found</p>
                    <p className="text-xs text-on-surface-variant">
                      No student records match the selected department or status filter.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              displayedRoster.map((student) => (
                <TableRow key={student.student_id}>
                  <TableCell className="font-mono font-semibold text-xs text-primary">
                    {student.rollNo}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <img
                        src={student.avatar}
                        alt={student.name}
                        className="w-8 h-8 rounded-full object-cover ring-1 ring-outline-variant bg-primary/10"
                      />
                      <div>
                        <p className="font-semibold text-xs text-on-surface">{student.name}</p>
                        <span className="text-[11px] text-on-surface-variant">
                          Year {student.year} ({student.section})
                        </span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-on-surface-variant">
                    {student.department}
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="inline-flex p-1 bg-surface-container rounded-lg gap-1">
                      <button
                        type="button"
                        onClick={() => handleStatusChange(student.student_id, 'Present')}
                        className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                          student.status === 'Present'
                            ? 'bg-emerald-600 text-white shadow-xs'
                            : 'text-on-surface-variant hover:text-on-surface'
                        }`}
                      >
                        Present
                      </button>
                      <button
                        type="button"
                        onClick={() => handleStatusChange(student.student_id, 'Absent')}
                        className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                          student.status === 'Absent'
                            ? 'bg-error text-white shadow-xs'
                            : 'text-on-surface-variant hover:text-on-surface'
                        }`}
                      >
                        Absent
                      </button>
                      <button
                        type="button"
                        onClick={() => handleStatusChange(student.student_id, 'Late')}
                        className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                          student.status === 'Late'
                            ? 'bg-amber-500 text-white shadow-xs'
                            : 'text-on-surface-variant hover:text-on-surface'
                        }`}
                      >
                        Late
                      </button>
                      <button
                        type="button"
                        onClick={() => handleStatusChange(student.student_id, 'Excused')}
                        className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                          student.status === 'Excused'
                            ? 'bg-blue-600 text-white shadow-xs'
                            : 'text-on-surface-variant hover:text-on-surface'
                        }`}
                      >
                        Excused
                      </button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      placeholder="Add remark..."
                      value={student.remarks}
                      onChange={(e) => handleRemarkChange(student.student_id, e.target.value)}
                      className="w-full text-xs px-2.5 py-1.5 bg-surface-container-low border border-outline-variant/40 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary focus:bg-white"
                    />
                  </TableCell>
                  {isAdmin && (
                    <TableCell className="text-right">
                      {student.attendanceId && (
                        <button
                          type="button"
                          onClick={() => setRecordToDelete(student)}
                          title="Delete Recorded Attendance"
                          className="p-1.5 text-on-surface-variant hover:text-error hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Delete Confirmation Modal (Admin only) */}
      {recordToDelete && isAdmin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-surface-container-lowest border border-outline-variant/80 rounded-2xl p-6 max-w-md w-full shadow-modal space-y-4">
            <div className="flex items-center gap-3 text-red-600">
              <div className="w-10 h-10 rounded-xl bg-red-50 border border-red-200 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-display font-bold text-base text-on-surface">Delete Attendance Record</h3>
                <p className="text-xs text-on-surface-variant">Permanent record removal</p>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
              Are you sure you want to delete the attendance record for <strong className="text-on-surface">{recordToDelete.name}</strong> on <strong className="text-on-surface">{sessionDate}</strong>?
            </p>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setRecordToDelete(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="container"
                size="sm"
                className="bg-red-600 hover:bg-red-700 text-white"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                icon={isDeleting ? Loader2 : Trash2}
              >
                {isDeleting ? 'Deleting...' : 'Confirm Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AttendancePage;

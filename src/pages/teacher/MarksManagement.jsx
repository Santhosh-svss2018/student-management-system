import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Award,
  Save,
  CheckCircle2,
  FileSpreadsheet,
  Plus,
  Edit2,
  Trash2,
  Search,
  RefreshCw,
  AlertCircle,
  Loader2,
  BookOpen,
  Filter,
  Check,
  AlertTriangle,
  GraduationCap
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Select from '../../components/common/Select';
import Input from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import Pagination from '../../components/common/Pagination';
import Table, { TableHead, TableBody, TableRow, TableCell } from '../../components/common/Table';
import { useAuth } from '../../context/AuthContext';
import { marksService } from '../../services/marksService';
import { studentService } from '../../services/studentService';

export function MarksManagement() {
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  // Filters State
  const [selectedCourse, setSelectedCourse] = useState('All');
  const [selectedExam, setSelectedExam] = useState('All');
  const [selectedSemester, setSelectedSemester] = useState('All');
  const [selectedYear, setSelectedYear] = useState('2024-2025');
  const [searchQuery, setSearchQuery] = useState('');

  // Data State
  const [marksList, setMarksList] = useState([]);
  const [students, setStudents] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    pages: 0,
  });

  // UI States
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  // Add Marks Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState(false);
  const [addFormError, setAddFormError] = useState(null);
  const [addFormData, setAddFormData] = useState({
    student_id: '',
    subject_code: 'CS-301',
    subject_name: 'Design & Analysis of Algorithms',
    semester: 5,
    exam_type: 'semester',
    marks_obtained: '',
    max_marks: 100,
    academic_year: '2024-2025',
    remarks: '',
  });

  // Edit Marks Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState(false);
  const [editFormError, setEditFormError] = useState(null);
  const [editingRecord, setEditingRecord] = useState(null);
  const [editFormData, setEditFormData] = useState({
    marks_obtained: '',
    max_marks: '',
    remarks: '',
  });

  // Delete Modal State (Admin only)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isSubmittingDelete, setIsSubmittingDelete] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);

  // Load students for mapping student names and IDs
  useEffect(() => {
    async function loadStudents() {
      try {
        const res = await studentService.getStudents(1, 100);
        setStudents(res?.items || []);
      } catch (err) {
        console.error('Failed to load students directory:', err);
      }
    }
    loadStudents();
  }, []);

  // Map of student_id -> student object
  const studentMap = useMemo(() => {
    const map = new Map();
    students.forEach((s) => {
      if (s.student_id) map.set(s.student_id, s);
      if (s.id) map.set(s.id, s);
      if (s.roll_number) map.set(s.roll_number, s);
    });
    return map;
  }, [students]);

  // Load marks from backend
  const fetchMarks = useCallback(async (page = 1) => {
    setIsLoading(true);
    setApiError(null);

    try {
      const params = {
        page,
        limit: pagination.limit,
      };

      if (selectedCourse !== 'All') params.subject_code = selectedCourse;
      if (selectedExam !== 'All') params.exam_type = selectedExam;
      if (selectedSemester !== 'All') params.semester = selectedSemester;
      if (selectedYear !== 'All') params.academic_year = selectedYear;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const res = await marksService.getMarks(params);
      setMarksList(res.items || []);
      setPagination({
        page: res.page || 1,
        limit: res.limit || 10,
        total: res.total || 0,
        pages: res.pages || 0,
      });
    } catch (err) {
      setApiError(err.message || 'Unable to fetch assessment marks records.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedCourse, selectedExam, selectedSemester, selectedYear, searchQuery, pagination.limit]);

  useEffect(() => {
    fetchMarks(1);
  }, [fetchMarks]);

  const showNotification = (message, type = 'success') => {
    setFeedback({ message, type });
    setTimeout(() => setFeedback(null), 5000);
  };

  // Open Add Modal
  const handleOpenAddModal = () => {
    setAddFormError(null);
    setAddFormData({
      student_id: students[0]?.student_id || '',
      subject_code: 'CS-301',
      subject_name: 'Design & Analysis of Algorithms',
      semester: 5,
      exam_type: 'semester',
      marks_obtained: '',
      max_marks: 100,
      academic_year: '2024-2025',
      remarks: '',
    });
    setIsAddModalOpen(true);
  };

  // Submit Add Marks
  const handleAddSubmit = async (e) => {
    e.preventDefault();
    setAddFormError(null);

    const obtainedNum = parseFloat(addFormData.marks_obtained);
    const maxNum = parseFloat(addFormData.max_marks);

    if (isNaN(obtainedNum) || obtainedNum < 0) {
      setAddFormError('Marks obtained must be a positive number.');
      return;
    }
    if (isNaN(maxNum) || maxNum <= 0) {
      setAddFormError('Maximum marks must be greater than 0.');
      return;
    }
    if (obtainedNum > maxNum) {
      setAddFormError(`Marks obtained (${obtainedNum}) cannot exceed maximum marks (${maxNum}).`);
      return;
    }
    if (!addFormData.student_id) {
      setAddFormError('Please select a student.');
      return;
    }

    setIsSubmittingAdd(true);
    try {
      const payload = {
        student_id: addFormData.student_id,
        subject_code: addFormData.subject_code.trim().toUpperCase(),
        subject_name: addFormData.subject_name.trim(),
        semester: parseInt(addFormData.semester, 10),
        exam_type: addFormData.exam_type,
        marks_obtained: obtainedNum,
        max_marks: maxNum,
        academic_year: addFormData.academic_year.trim(),
        remarks: addFormData.remarks.trim() || undefined,
      };

      const created = await marksService.createMarks(payload);
      setIsAddModalOpen(false);
      showNotification(`Marks recorded successfully: Grade ${created.grade} (${created.percentage}%)`);
      fetchMarks(pagination.page);
    } catch (err) {
      if (err.status === 409) {
        setAddFormError('Marks already exist for this student, subject, semester, exam type, and academic year.');
      } else {
        setAddFormError(err.message || 'Failed to record marks.');
      }
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Open Edit Modal
  const handleOpenEditModal = (record) => {
    setEditingRecord(record);
    setEditFormError(null);
    setEditFormData({
      marks_obtained: record.marks_obtained,
      max_marks: record.max_marks,
      remarks: record.remarks || '',
    });
    setIsEditModalOpen(true);
  };

  // Submit Edit Marks
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!editingRecord) return;
    setEditFormError(null);

    const obtainedNum = parseFloat(editFormData.marks_obtained);
    const maxNum = parseFloat(editFormData.max_marks);

    if (isNaN(obtainedNum) || obtainedNum < 0) {
      setEditFormError('Marks obtained must be a positive number.');
      return;
    }
    if (isNaN(maxNum) || maxNum <= 0) {
      setEditFormError('Maximum marks must be greater than 0.');
      return;
    }
    if (obtainedNum > maxNum) {
      setEditFormError(`Marks obtained (${obtainedNum}) cannot exceed maximum marks (${maxNum}).`);
      return;
    }

    setIsSubmittingEdit(true);
    try {
      const payload = {
        marks_obtained: obtainedNum,
        max_marks: maxNum,
        remarks: editFormData.remarks.trim() || undefined,
      };

      const updated = await marksService.updateMarks(editingRecord.marks_id, payload);
      setIsEditModalOpen(false);
      showNotification(`Marks updated successfully: Grade ${updated.grade} (${updated.percentage}%)`);
      fetchMarks(pagination.page);
    } catch (err) {
      setEditFormError(err.message || 'Failed to update marks.');
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Open Delete Modal (Admin only)
  const handleOpenDeleteModal = (record) => {
    setRecordToDelete(record);
    setIsDeleteModalOpen(true);
  };

  // Confirm Delete
  const handleDeleteConfirm = async () => {
    if (!recordToDelete) return;

    setIsSubmittingDelete(true);
    try {
      await marksService.deleteMarks(recordToDelete.marks_id);
      setIsDeleteModalOpen(false);
      showNotification(`Marks record ${recordToDelete.marks_id} deleted permanently.`);
      fetchMarks(pagination.page);
    } catch (err) {
      showNotification(err.message || 'Failed to delete marks record.', 'error');
    } finally {
      setIsSubmittingDelete(false);
    }
  };

  // Format Exam Type Label
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

  // Subject code to name mapping preset
  const handleCourseSelectChange = (code) => {
    const courseMap = {
      'CS-301': 'Design & Analysis of Algorithms',
      'CS-402': 'Cloud Architecture & DevOps',
      'CS-305': 'AI & Machine Learning Lab',
      'CS-302': 'Database Management Systems',
      'CS-303': 'Operating Systems',
    };
    setAddFormData((prev) => ({
      ...prev,
      subject_code: code,
      subject_name: courseMap[code] || prev.subject_name,
    }));
  };

  // Helper for grade styling
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

  return (
    <div className="space-y-6">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface flex items-center gap-2.5">
            <Award className="w-6 h-6 text-primary" />
            Marks Management & Grade Evaluation
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Record assessment marks, review automatic grade distributions, and evaluate student academic standing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={() => fetchMarks(pagination.page)}
            disabled={isLoading}
          >
            Refresh
          </Button>
          <Button
            variant="container"
            size="sm"
            icon={Plus}
            onClick={handleOpenAddModal}
          >
            Record Marks
          </Button>
        </div>
      </div>

      {/* Success / Feedback Banner */}
      {feedback && (
        <div className={`p-4 rounded-xl flex items-center gap-3 text-xs sm:text-sm animate-in fade-in ${
          feedback.type === 'error'
            ? 'bg-red-50 border border-red-200 text-error'
            : 'bg-emerald-50 border border-emerald-200 text-tertiary'
        }`}>
          {feedback.type === 'error' ? (
            <AlertCircle className="w-5 h-5 flex-shrink-0 text-error" />
          ) : (
            <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-tertiary" />
          )}
          <span className="font-semibold">{feedback.message}</span>
        </div>
      )}

      {/* API Error Banner */}
      {apiError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-error text-xs sm:text-sm animate-in fade-in">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="font-semibold">{apiError}</span>
        </div>
      )}

      {/* Filter & Scheme Card */}
      <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Select
          label="Course / Subject"
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
          options={[
            { label: 'All Courses', value: 'All' },
            { label: 'CS-301: Design & Analysis of Algorithms', value: 'CS-301' },
            { label: 'CS-402: Cloud Architecture & DevOps', value: 'CS-402' },
            { label: 'CS-305: AI & Machine Learning Lab', value: 'CS-305' },
            { label: 'CS-302: Database Management Systems', value: 'CS-302' },
            { label: 'CS-303: Operating Systems', value: 'CS-303' }
          ]}
        />
        <Select
          label="Assessment Component"
          value={selectedExam}
          onChange={(e) => setSelectedExam(e.target.value)}
          options={[
            { label: 'All Components', value: 'All' },
            { label: 'Semester Final Exam', value: 'semester' },
            { label: 'Internal Assessment 1', value: 'internal_1' },
            { label: 'Internal Assessment 2', value: 'internal_2' },
            { label: 'Model Examination', value: 'model' },
            { label: 'Assignment / Project', value: 'assignment' }
          ]}
        />
        <Select
          label="Academic Semester"
          value={selectedSemester}
          onChange={(e) => setSelectedSemester(e.target.value)}
          options={[
            { label: 'All Semesters', value: 'All' },
            { label: 'Semester 1', value: '1' },
            { label: 'Semester 2', value: '2' },
            { label: 'Semester 3', value: '3' },
            { label: 'Semester 4', value: '4' },
            { label: 'Semester 5', value: '5' },
            { label: 'Semester 6', value: '6' },
            { label: 'Semester 7', value: '7' },
            { label: 'Semester 8', value: '8' }
          ]}
        />
        <Select
          label="Academic Year"
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target.value)}
          options={[
            { label: 'All Academic Years', value: 'All' },
            { label: '2024 - 2025', value: '2024-2025' },
            { label: '2025 - 2026', value: '2025-2026' }
          ]}
        />
        <div className="flex flex-col justify-center bg-blue-50/70 p-3 rounded-lg border border-blue-200/60">
          <span className="text-[10px] font-bold text-blue-900 uppercase">Grading Scale (Authoritative)</span>
          <span className="text-[11px] text-blue-700 font-semibold mt-0.5">
            A+: 90%+ | A: 80% | B: 70% | C: 60% | Pass: 40%
          </span>
        </div>
      </div>

      {/* Marks Table */}
      <Card
        title="Student Assessment Scores"
        subtitle={`MongoDB Atlas Records • Total: ${pagination.total} Evaluation${pagination.total === 1 ? '' : 's'}`}
        padding="none"
      >
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant space-y-2">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <p className="text-xs font-semibold">Synchronizing marks records from backend API...</p>
          </div>
        ) : marksList.length === 0 ? (
          <div className="py-16 text-center space-y-3">
            <BookOpen className="w-10 h-10 text-on-surface-variant/40 mx-auto" />
            <p className="text-sm font-semibold text-on-surface">No marks records found.</p>
            <p className="text-xs text-on-surface-variant max-w-sm mx-auto">
              No evaluations match the selected filters. Click "Record Marks" above to submit assessment scores.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHead>
                <TableRow hoverable={false}>
                  <TableCell as="th">Student / Roll No</TableCell>
                  <TableCell as="th">Subject / Course</TableCell>
                  <TableCell as="th" className="text-center">Semester</TableCell>
                  <TableCell as="th">Assessment</TableCell>
                  <TableCell as="th" className="text-center">Score</TableCell>
                  <TableCell as="th" className="text-center">Percentage</TableCell>
                  <TableCell as="th" className="text-center">Grade</TableCell>
                  <TableCell as="th">Evaluator</TableCell>
                  <TableCell as="th" className="text-right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {marksList.map((row) => {
                  const student = studentMap.get(row.student_id);
                  const displayName = student?.full_name || student?.name || row.student_id;
                  const rollNumber = student?.roll_number || row.student_id;

                  return (
                    <TableRow key={row.marks_id || row.id}>
                      <TableCell>
                        <div className="font-semibold text-xs text-on-surface">{displayName}</div>
                        <div className="font-mono text-[11px] text-primary mt-0.5">{rollNumber}</div>
                      </TableCell>
                      <TableCell>
                        <div className="font-semibold text-xs text-on-surface">{row.subject_code}</div>
                        <div className="text-[11px] text-on-surface-variant truncate max-w-[180px]">{row.subject_name}</div>
                      </TableCell>
                      <TableCell className="text-center font-semibold text-xs text-on-surface">
                        Sem {row.semester}
                      </TableCell>
                      <TableCell>
                        <Badge variant="primary" size="sm">
                          {formatExamType(row.exam_type)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center font-bold text-xs text-on-surface">
                        {row.marks_obtained} / {row.max_marks}
                      </TableCell>
                      <TableCell className="text-center font-bold text-xs text-primary">
                        {row.percentage}%
                      </TableCell>
                      <TableCell className="text-center">
                        {getGradeBadge(row.grade)}
                      </TableCell>
                      <TableCell className="text-xs text-on-surface-variant font-mono">
                        {row.entered_by ? row.entered_by.split('@')[0] : 'Admin'}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleOpenEditModal(row)}
                            title="Edit Marks"
                            className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          {isAdmin && (
                            <button
                              onClick={() => handleOpenDeleteModal(row)}
                              title="Delete Marks (Admin only)"
                              className="p-1.5 text-on-surface-variant hover:text-error hover:bg-error/10 rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4 text-error" />
                            </button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}

        {pagination.pages > 1 && (
          <Pagination
            currentPage={pagination.page}
            totalPages={pagination.pages}
            totalItems={pagination.total}
            pageSize={pagination.limit}
            onPageChange={(p) => fetchMarks(p)}
          />
        )}
      </Card>

      {/* Add Marks Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Record Student Assessment Marks"
        subtitle="Submit evaluation scores with automatic backend percentage and grade calculation."
        maxWidth="max-w-xl"
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAddModalOpen(false)}
              disabled={isSubmittingAdd}
            >
              Cancel
            </Button>
            <Button
              variant="container"
              size="sm"
              onClick={handleAddSubmit}
              disabled={isSubmittingAdd}
            >
              {isSubmittingAdd ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                  Recording...
                </>
              ) : (
                'Save & Submit'
              )}
            </Button>
          </>
        }
      >
        <form onSubmit={handleAddSubmit} className="space-y-4">
          {addFormError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-error text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{addFormError}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-on-surface mb-1">
              Select Student *
            </label>
            <select
              value={addFormData.student_id}
              onChange={(e) => setAddFormData({ ...addFormData, student_id: e.target.value })}
              className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
              required
            >
              <option value="">-- Choose Student --</option>
              {students.map((s) => (
                <option key={s.id || s.student_id} value={s.student_id}>
                  {s.full_name || s.name} ({s.roll_number || s.student_id}) - {s.department}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Course Code *</label>
              <select
                value={addFormData.subject_code}
                onChange={(e) => handleCourseSelectChange(e.target.value)}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
              >
                <option value="CS-301">CS-301: Algorithms</option>
                <option value="CS-402">CS-402: Cloud Architecture</option>
                <option value="CS-305">CS-305: AI & ML Lab</option>
                <option value="CS-302">CS-302: DBMS</option>
                <option value="CS-303">CS-303: Operating Systems</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Subject Title *</label>
              <input
                type="text"
                value={addFormData.subject_name}
                onChange={(e) => setAddFormData({ ...addFormData, subject_name: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Semester (1-8) *</label>
              <input
                type="number"
                min="1"
                max="8"
                value={addFormData.semester}
                onChange={(e) => setAddFormData({ ...addFormData, semester: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Exam Type *</label>
              <select
                value={addFormData.exam_type}
                onChange={(e) => setAddFormData({ ...addFormData, exam_type: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
              >
                <option value="semester">Semester Final</option>
                <option value="internal_1">Internal 1</option>
                <option value="internal_2">Internal 2</option>
                <option value="model">Model Exam</option>
                <option value="assignment">Assignment</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Academic Year *</label>
              <input
                type="text"
                value={addFormData.academic_year}
                onChange={(e) => setAddFormData({ ...addFormData, academic_year: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                placeholder="2024-2025"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Marks Obtained *</label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={addFormData.marks_obtained}
                onChange={(e) => setAddFormData({ ...addFormData, marks_obtained: e.target.value })}
                placeholder="e.g. 85"
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Maximum Marks *</label>
              <input
                type="number"
                step="0.1"
                min="1"
                value={addFormData.max_marks}
                onChange={(e) => setAddFormData({ ...addFormData, max_marks: e.target.value })}
                placeholder="e.g. 100"
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface mb-1">Remarks (Optional)</label>
            <input
              type="text"
              value={addFormData.remarks}
              onChange={(e) => setAddFormData({ ...addFormData, remarks: e.target.value })}
              placeholder="e.g. Excellent algorithmic problem solving"
              className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
            />
          </div>
        </form>
      </Modal>

      {/* Edit Marks Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Modify Assessment Marks"
        subtitle={`Updating scores for ${editingRecord?.subject_code} • ${editingRecord?.student_id}`}
        maxWidth="max-w-md"
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditModalOpen(false)}
              disabled={isSubmittingEdit}
            >
              Cancel
            </Button>
            <Button
              variant="container"
              size="sm"
              onClick={handleEditSubmit}
              disabled={isSubmittingEdit}
            >
              {isSubmittingEdit ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                  Saving...
                </>
              ) : (
                'Update Score'
              )}
            </Button>
          </>
        }
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          {editFormError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-error text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{editFormError}</span>
            </div>
          )}

          <div className="p-3 bg-surface-container-low rounded-xl text-xs space-y-1 text-on-surface-variant">
            <div className="flex justify-between">
              <span className="font-semibold text-on-surface">Subject:</span>
              <span>{editingRecord?.subject_code} - {editingRecord?.subject_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-semibold text-on-surface">Assessment:</span>
              <span>{editingRecord?.exam_type ? formatExamType(editingRecord.exam_type) : ''} (Sem {editingRecord?.semester})</span>
            </div>
            <div className="flex justify-between">
              <span className="font-semibold text-on-surface">Academic Year:</span>
              <span>{editingRecord?.academic_year}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Marks Obtained *</label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={editFormData.marks_obtained}
                onChange={(e) => setEditFormData({ ...editFormData, marks_obtained: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Max Marks *</label>
              <input
                type="number"
                step="0.1"
                min="1"
                value={editFormData.max_marks}
                onChange={(e) => setEditFormData({ ...editFormData, max_marks: e.target.value })}
                className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface mb-1">Remarks</label>
            <input
              type="text"
              value={editFormData.remarks}
              onChange={(e) => setEditFormData({ ...editFormData, remarks: e.target.value })}
              className="w-full text-xs py-2 px-3 bg-surface-container-low border border-outline-variant/40 rounded-xl focus:bg-white focus:ring-1 focus:ring-primary focus:outline-none"
            />
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal (Admin only) */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Assessment Marks Record"
        maxWidth="max-w-md"
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsDeleteModalOpen(false)}
              disabled={isSubmittingDelete}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleDeleteConfirm}
              disabled={isSubmittingDelete}
            >
              {isSubmittingDelete ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                  Deleting...
                </>
              ) : (
                'Delete Record'
              )}
            </Button>
          </>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-xl text-error text-xs">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p>
              Are you sure you want to permanently delete marks for{' '}
              <strong className="font-semibold text-on-surface">
                {recordToDelete?.student_id} ({recordToDelete?.subject_code})
              </strong>? This action cannot be undone.
            </p>
          </div>
          <p className="text-xs text-on-surface-variant">
            Marks ID: <span className="font-mono text-on-surface">{recordToDelete?.marks_id}</span>
          </p>
        </div>
      </Modal>
    </div>
  );
}

export default MarksManagement;

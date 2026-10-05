import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  UserPlus,
  Search,
  Filter,
  Download,
  Eye,
  Edit,
  Trash2,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Loader2,
  XCircle,
  AlertTriangle,
  Key
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Input from '../../components/common/Input';
import Select from '../../components/common/Select';
import Tabs from '../../components/common/Tabs';
import Table, { TableHead, TableBody, TableRow, TableCell } from '../../components/common/Table';
import Pagination from '../../components/common/Pagination';
import ChangePasswordModal from '../../components/common/ChangePasswordModal';
import { useAuth } from '../../context/AuthContext';
import { studentService } from '../../services/studentService';

export function StudentDirectory() {
  const navigate = useNavigate();
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  // State
  const [students, setStudents] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [activeTab, setActiveTab] = useState('all');

  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  // Password management modal state
  const [passwordTargetStudent, setPasswordTargetStudent] = useState(null);

  // Deactivation confirmation modal state
  const [studentToDeactivate, setStudentToDeactivate] = useState(null);
  const [isDeactivating, setIsDeactivating] = useState(false);

  // Debounce search input (350ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setCurrentPage(1); // Reset to page 1 on new search
    }, 350);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch students from backend
  const fetchStudents = useCallback(async () => {
    setIsLoading(true);
    setApiError(null);

    try {
      const response = await studentService.getStudents(currentPage, pageSize, debouncedSearch);
      if (response) {
        setStudents(response.items || []);
        setTotalItems(response.total || 0);
        setTotalPages(response.pages || 1);
      }
    } catch (err) {
      setApiError(err.message || 'Failed to load students from the server.');
      setStudents([]);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch]);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  // Client-side filtering for department and tabs
  const displayedStudents = useMemo(() => {
    return students.filter((student) => {
      const dept = student.department || '';
      const matchDept = selectedDept === 'All' || dept.toLowerCase().includes(selectedDept.toLowerCase());

      const isActive = student.is_active !== false;
      const matchTab =
        activeTab === 'all' ? true :
        activeTab === 'active' ? isActive :
        activeTab === 'inactive' ? !isActive : true;

      return matchDept && matchTab;
    });
  }, [students, selectedDept, activeTab]);

  const activeCount = useMemo(() => students.filter(s => s.is_active !== false).length, [students]);
  const inactiveCount = useMemo(() => students.filter(s => s.is_active === false).length, [students]);

  const tabs = [
    { id: 'all', label: 'All Students', count: totalItems },
    { id: 'active', label: 'Active', count: activeCount },
    { id: 'inactive', label: 'Inactive', count: inactiveCount },
  ];

  // Handle student deactivation (Soft-delete)
  const handleConfirmDeactivate = async () => {
    if (!studentToDeactivate) return;
    setIsDeactivating(true);

    try {
      const identifier = studentToDeactivate.student_id || studentToDeactivate.id;
      await studentService.deactivateStudent(identifier);

      setFeedback({
        type: 'success',
        message: `Student "${studentToDeactivate.full_name || studentToDeactivate.name}" was deactivated successfully.`
      });
      setStudentToDeactivate(null);
      await fetchStudents();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to deactivate student record.'
      });
    } finally {
      setIsDeactivating(false);
    }
  };

  // Helper for generating avatar
  const getAvatar = (student) => {
    const name = student.full_name || student.name || 'Student';
    return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(name)}&backgroundColor=004494,0066cc,2563eb`;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface flex items-center gap-2.5">
            <Users className="w-6 h-6 text-primary" />
            Student Management Directory
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Search, filter, manage enrollments and view detailed academic records.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={fetchStudents}
            disabled={isLoading}
          >
            Refresh
          </Button>

          {/* Add Student button: Admin only */}
          {isAdmin && (
            <Button
              variant="container"
              size="sm"
              icon={UserPlus}
              onClick={() => navigate('/students/new')}
            >
              Add Student
            </Button>
          )}
        </div>
      </div>

      {/* Feedback Toast Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-sm animate-in fade-in ${
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

      {/* API Error State */}
      {apiError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between gap-3 text-error text-sm">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Unable to fetch students</p>
              <p className="text-xs mt-0.5 text-red-700">{apiError}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={fetchStudents}>
            Retry
          </Button>
        </div>
      )}

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} variant="pills" />

      {/* Filter & Search Bar */}
      <div className="p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="sm:col-span-2">
          <Input
            icon={Search}
            placeholder="Search by name, roll no, email, student ID, department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div>
          <Select
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
        </div>
      </div>

      {/* Student Records Table */}
      <Card padding="none">
        <Table>
          <TableHead>
            <TableRow hoverable={false}>
              <TableCell as="th">Student</TableCell>
              <TableCell as="th">Student ID / Roll No</TableCell>
              <TableCell as="th">Department</TableCell>
              <TableCell as="th">Year / Section</TableCell>
              <TableCell as="th">Phone</TableCell>
              <TableCell as="th">Status</TableCell>
              <TableCell as="th" className="text-right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow hoverable={false}>
                <TableCell colSpan={7} className="text-center py-12 text-on-surface-variant">
                  <div className="flex flex-col items-center justify-center gap-3">
                    <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    <p className="text-xs font-semibold">Loading student records from server...</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : displayedStudents.length === 0 ? (
              <TableRow hoverable={false}>
                <TableCell colSpan={7} className="text-center py-12 text-on-surface-variant">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Users className="w-10 h-10 text-on-surface-variant/40" />
                    <p className="font-semibold text-sm text-on-surface">No students found</p>
                    <p className="text-xs text-on-surface-variant max-w-sm">
                      {searchTerm
                        ? `No students matched your search query "${searchTerm}".`
                        : 'No student records exist in the system yet.'}
                    </p>
                    {isAdmin && !searchTerm && (
                      <Button
                        variant="container"
                        size="sm"
                        icon={UserPlus}
                        className="mt-3"
                        onClick={() => navigate('/students/new')}
                      >
                        Add First Student
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              displayedStudents.map((student) => {
                const targetId = student.student_id || student.id;
                const isActive = student.is_active !== false;

                return (
                  <TableRow
                    key={student.id || student.student_id}
                    onClick={() => navigate(`/students/${targetId}`)}
                  >
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <img
                          src={getAvatar(student)}
                          alt={student.full_name || student.name}
                          className="w-9 h-9 rounded-full object-cover ring-1 ring-primary/20 bg-primary/10"
                        />
                        <div>
                          <p className="font-bold text-xs sm:text-sm text-on-surface">
                            {student.full_name || student.name}
                          </p>
                          <p className="text-[11px] text-on-surface-variant">{student.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono font-semibold text-xs text-primary">
                      <div>
                        <span>{student.roll_number || student.rollNo}</span>
                        {student.student_id && student.student_id !== (student.roll_number || student.rollNo) && (
                          <span className="block text-[10px] text-on-surface-variant font-normal">
                            ID: {student.student_id}
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-xs text-on-surface">
                      {student.department}
                    </TableCell>
                    <TableCell className="text-xs font-medium">
                      Year {student.year || 1} {student.section ? `(${student.section})` : ''}
                    </TableCell>
                    <TableCell className="text-xs text-on-surface-variant">
                      {student.phone || '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="status" size="sm" dot>
                        {isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1">
                        {/* View Profile: Admin & Teacher */}
                        <button
                          onClick={() => navigate(`/students/${targetId}`)}
                          title="View Profile"
                          className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-lg transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>

                        {/* Change Password: Admin only */}
                        {isAdmin && (
                          <button
                            onClick={() => setPasswordTargetStudent(student)}
                            title="Change Password"
                            className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                          >
                            <Key className="w-4 h-4" />
                          </button>
                        )}

                        {/* Edit: Admin only */}
                        {isAdmin && (
                          <button
                            onClick={() => navigate(`/students/${targetId}/edit`)}
                            title="Edit Student"
                            className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                        )}

                        {/* Deactivate: Admin only */}
                        {isAdmin && isActive && (
                          <button
                            onClick={() => setStudentToDeactivate(student)}
                            title="Deactivate Student"
                            className="p-1.5 text-on-surface-variant hover:text-error hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Pagination */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          pageSize={pageSize}
          onPageChange={setCurrentPage}
        />
      </Card>

      {/* Admin Password Management Dialog */}
      {isAdmin && passwordTargetStudent && (
        <ChangePasswordModal
          isOpen={Boolean(passwordTargetStudent)}
          onClose={() => setPasswordTargetStudent(null)}
          targetUser={passwordTargetStudent}
        />
      )}

      {/* Deactivate Confirmation Modal */}
      {studentToDeactivate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-surface-container-lowest border border-outline-variant/80 rounded-2xl p-6 max-w-md w-full shadow-modal space-y-4">
            <div className="flex items-center gap-3 text-amber-600">
              <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-display font-bold text-base text-on-surface">Deactivate Student</h3>
                <p className="text-xs text-on-surface-variant">Soft delete student record</p>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
              Are you sure you want to deactivate <strong className="text-on-surface">{studentToDeactivate.full_name || studentToDeactivate.name}</strong> ({studentToDeactivate.roll_number || studentToDeactivate.student_id})? This will mark their enrollment as inactive.
            </p>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setStudentToDeactivate(null)}
                disabled={isDeactivating}
              >
                Cancel
              </Button>
              <Button
                variant="container"
                size="sm"
                className="bg-red-600 hover:bg-red-700 text-white"
                onClick={handleConfirmDeactivate}
                disabled={isDeactivating}
                icon={isDeactivating ? Loader2 : Trash2}
              >
                {isDeactivating ? 'Deactivating...' : 'Confirm Deactivate'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StudentDirectory;

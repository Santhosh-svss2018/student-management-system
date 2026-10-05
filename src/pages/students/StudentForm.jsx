import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  UserPlus,
  Save,
  ArrowLeft,
  UploadCloud,
  CheckCircle2,
  FileText,
  User,
  GraduationCap,
  Users,
  Paperclip,
  AlertCircle,
  Loader2,
  Key
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Textarea } from '../../components/common/Input';
import Select from '../../components/common/Select';
import Tabs from '../../components/common/Tabs';
import { studentService } from '../../services/studentService';

export function StudentForm({ mode = 'add' }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = mode === 'edit' || Boolean(id);

  const [activeTab, setActiveTab] = useState('personal');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingInitial, setIsLoadingInitial] = useState(isEdit);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    dob: '2004-05-14',
    gender: 'Male',
    bloodGroup: 'O+',
    address: '',
    student_id: '',
    rollNo: '',
    department: 'Computer Science & Engineering',
    program: 'B.Tech',
    batch: '2022 - 2026',
    year: '3',
    semester: '6th Semester',
    section: 'CS-A',
    is_active: true,
    admissionCategory: 'Merit',
    guardianName: '',
    guardianRelation: 'Father',
    guardianPhone: '',
    guardianEmail: '',
    guardianOccupation: '',
    initial_password: '',
    confirm_password: ''
  });

  // Fetch existing student for Edit mode
  useEffect(() => {
    let isMounted = true;

    async function loadStudentData() {
      if (!isEdit || !id) {
        setIsLoadingInitial(false);
        return;
      }

      setIsLoadingInitial(true);
      setErrorMessage(null);

      try {
        const student = await studentService.getStudent(id);
        if (isMounted && student) {
          setFormData({
            name: student.full_name || '',
            email: student.email || '',
            phone: student.phone || '',
            dob: student.date_of_birth || '2004-05-14',
            gender: student.gender || 'Male',
            bloodGroup: 'O+',
            address: student.address || '',
            student_id: student.student_id || '',
            rollNo: student.roll_number || student.student_id || '',
            department: student.department || 'Computer Science & Engineering',
            program: 'B.Tech',
            batch: '2022 - 2026',
            year: String(student.year || 3),
            semester: `${(student.year || 3) * 2}th Semester`,
            section: student.section || 'CS-A',
            is_active: student.is_active !== false,
            admissionCategory: 'Merit',
            guardianName: '',
            guardianRelation: 'Father',
            guardianPhone: '',
            guardianEmail: '',
            guardianOccupation: ''
          });
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage(err.message || `Failed to load student record with identifier "${id}".`);
        }
      } finally {
        if (isMounted) {
          setIsLoadingInitial(false);
        }
      }
    }

    loadStudentData();

    return () => {
      isMounted = false;
    };
  }, [isEdit, id]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errorMessage) setErrorMessage(null);
  };

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    // Basic client-side validation
    if (!formData.name?.trim()) {
      setErrorMessage('Full name is required.');
      setIsSubmitting(false);
      return;
    }
    if (!formData.email?.trim()) {
      setErrorMessage('Email address is required.');
      setIsSubmitting(false);
      return;
    }
    if (!formData.rollNo?.trim()) {
      setErrorMessage('Roll Number is required.');
      setIsSubmitting(false);
      return;
    }

    const yearNumber = parseInt(formData.year, 10) || 1;

    try {
      if (isEdit) {
        // Update Payload
        const updatePayload = {
          full_name: formData.name.trim(),
          email: formData.email.trim().toLowerCase(),
          phone: formData.phone?.trim() || null,
          date_of_birth: formData.dob || null,
          gender: formData.gender || null,
          department: formData.department?.trim() || 'Computer Science & Engineering',
          year: yearNumber,
          section: formData.section?.trim() || null,
          roll_number: formData.rollNo.trim(),
          address: formData.address?.trim() || null,
          is_active: Boolean(formData.is_active)
        };

        if (formData.student_id?.trim()) {
          updatePayload.student_id = formData.student_id.trim();
        }

        await studentService.updateStudent(id, updatePayload);
        setSavedSuccess(true);
      } else {
        // Initial password validation if supplied
        if (formData.initial_password && formData.initial_password.trim()) {
          if (formData.initial_password.trim().length < 8) {
            setErrorMessage('Initial login password must be at least 8 characters long.');
            setIsSubmitting(false);
            return;
          }
          if (formData.initial_password !== formData.confirm_password) {
            setErrorMessage('Initial login passwords do not match. Please verify.');
            setIsSubmitting(false);
            return;
          }
        }

        // Create Payload
        const createPayload = {
          student_id: (formData.student_id || formData.rollNo).trim(),
          full_name: formData.name.trim(),
          email: formData.email.trim().toLowerCase(),
          phone: formData.phone?.trim() || null,
          date_of_birth: formData.dob || null,
          gender: formData.gender || null,
          department: formData.department?.trim() || 'Computer Science & Engineering',
          year: yearNumber,
          section: formData.section?.trim() || null,
          roll_number: formData.rollNo.trim(),
          address: formData.address?.trim() || null,
          is_active: Boolean(formData.is_active)
        };

        if (formData.initial_password && formData.initial_password.trim()) {
          createPayload.initial_password = formData.initial_password.trim();
        }

        await studentService.createStudent(createPayload);
        setSavedSuccess(true);
      }

      // Navigate back after short visual feedback
      setTimeout(() => {
        navigate('/students');
      }, 1200);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to save student record.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabs = [
    { id: 'personal', label: '1. Personal Information', icon: User },
    { id: 'academic', label: '2. Academic Details', icon: GraduationCap },
    { id: 'guardian', label: '3. Guardian & Contact', icon: Users },
    { id: 'documents', label: '4. Documents & Uploads', icon: Paperclip },
  ];

  if (isLoadingInitial) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-3">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <p className="text-xs font-semibold text-on-surface-variant">Loading student profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => navigate(-1)}>
            Back
          </Button>
          <div>
            <h1 className="font-display text-2xl font-bold text-on-surface">
              {isEdit ? `Edit Student: ${formData.name || 'Student Profile'}` : 'Register New Student'}
            </h1>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
              {isEdit
                ? 'Update student demographic and academic records'
                : 'Fill in the details to enroll a new student into the university system'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/students')} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="container"
            size="sm"
            icon={isSubmitting ? Loader2 : Save}
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : isEdit ? 'Save Changes' : 'Enroll Student'}
          </Button>
        </div>
      </div>

      {/* Success Notification */}
      {savedSuccess && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-3 text-tertiary text-sm animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span className="font-semibold">
            {isEdit
              ? 'Student record successfully updated! Redirecting...'
              : 'New student successfully registered and enrolled! Redirecting...'}
          </span>
        </div>
      )}

      {/* Error Notification */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between gap-3 text-error text-sm animate-in fade-in">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="font-semibold">{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="p-1 hover:opacity-70 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <form onSubmit={handleSubmit}>
        {/* Tab 1: Personal Info */}
        {activeTab === 'personal' && (
          <Card title="Personal & Demographic Details">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Legal Name"
                placeholder="e.g. Arun Kumar"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                required
              />
              <Input
                label="Institutional Email"
                type="email"
                placeholder="name@student.edumanage.edu"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                required
              />
              <Input
                label="Mobile Phone Number"
                placeholder="+91 98765 43210"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
              />
              <Input
                label="Date of Birth"
                type="date"
                value={formData.dob}
                onChange={(e) => handleChange('dob', e.target.value)}
              />
              <Select
                label="Gender"
                value={formData.gender}
                onChange={(e) => handleChange('gender', e.target.value)}
                options={['Male', 'Female', 'Non-Binary', 'Prefer not to say']}
              />
              <Select
                label="Blood Group"
                value={formData.bloodGroup}
                onChange={(e) => handleChange('bloodGroup', e.target.value)}
                options={['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']}
              />
              <div className="sm:col-span-2">
                <Textarea
                  label="Permanent Residential Address"
                  placeholder="Street address, City, State, ZIP code"
                  value={formData.address}
                  onChange={(e) => handleChange('address', e.target.value)}
                  rows={2}
                />
              </div>

              {/* Optional Initial Portal Password (New Enrollment Only) */}
              {!isEdit && (
                <div className="sm:col-span-2 pt-4 border-t border-outline-variant/40">
                  <h4 className="font-bold text-xs text-on-surface mb-1 flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5 text-primary" />
                    Student Authentication & Portal Password (Optional)
                  </h4>
                  <p className="text-[11px] text-on-surface-variant mb-3 leading-relaxed">
                    Set an initial password for the student account. If omitted, a default password (<span className="font-mono text-primary font-semibold">EduManage@&lt;StudentID&gt;</span>) is automatically generated and can be changed anytime by an Admin.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Input
                      label="Initial Login Password"
                      type="password"
                      placeholder="Min. 8 characters (optional)"
                      value={formData.initial_password || ''}
                      onChange={(e) => handleChange('initial_password', e.target.value)}
                    />
                    <Input
                      label="Confirm Initial Password"
                      type="password"
                      placeholder="Confirm initial password"
                      value={formData.confirm_password || ''}
                      onChange={(e) => handleChange('confirm_password', e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="flex justify-end mt-6">
              <Button variant="primary" size="sm" type="button" onClick={() => setActiveTab('academic')}>
                Next: Academic Details
              </Button>
            </div>
          </Card>
        )}

        {/* Tab 2: Academic Info */}
        {activeTab === 'academic' && (
          <Card title="Academic & Enrollment Information">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Roll Number"
                placeholder="e.g. CS-22-089"
                value={formData.rollNo}
                onChange={(e) => handleChange('rollNo', e.target.value)}
                required
              />
              <Input
                label="Institutional Student ID"
                placeholder="e.g. STU-2024-089 (optional, defaults to Roll No)"
                value={formData.student_id}
                onChange={(e) => handleChange('student_id', e.target.value)}
              />
              <Select
                label="Department"
                value={formData.department}
                onChange={(e) => handleChange('department', e.target.value)}
                options={[
                  'Computer Science & Engineering',
                  'Information Technology',
                  'Electronics & Communication',
                  'Mechanical Engineering',
                  'Civil Engineering'
                ]}
              />
              <Select
                label="Academic Year"
                value={formData.year}
                onChange={(e) => handleChange('year', e.target.value)}
                options={[
                  { label: 'Year 1 (1st/2nd Semester)', value: '1' },
                  { label: 'Year 2 (3rd/4th Semester)', value: '2' },
                  { label: 'Year 3 (5th/6th Semester)', value: '3' },
                  { label: 'Year 4 (7th/8th Semester)', value: '4' }
                ]}
              />
              <Select
                label="Class Section"
                value={formData.section}
                onChange={(e) => handleChange('section', e.target.value)}
                options={['CS-A', 'CS-B', 'CS-C', 'IT-A', 'IT-B', 'EC-A', 'ME-A', 'CE-A']}
              />
              <Select
                label="Enrollment Status"
                value={formData.is_active ? 'Active' : 'Inactive'}
                onChange={(e) => handleChange('is_active', e.target.value === 'Active')}
                options={['Active', 'Inactive']}
              />
            </div>
            <div className="flex justify-between mt-6">
              <Button variant="outline" size="sm" type="button" onClick={() => setActiveTab('personal')}>
                Previous
              </Button>
              <Button variant="primary" size="sm" type="button" onClick={() => setActiveTab('guardian')}>
                Next: Guardian Details
              </Button>
            </div>
          </Card>
        )}

        {/* Tab 3: Guardian Details */}
        {activeTab === 'guardian' && (
          <Card title="Parent / Guardian & Emergency Contact">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Guardian Full Name"
                placeholder="e.g. Rajesh Kumar"
                value={formData.guardianName}
                onChange={(e) => handleChange('guardianName', e.target.value)}
              />
              <Select
                label="Relationship"
                value={formData.guardianRelation}
                onChange={(e) => handleChange('guardianRelation', e.target.value)}
                options={['Father', 'Mother', 'Legal Guardian', 'Sibling']}
              />
              <Input
                label="Guardian Phone"
                placeholder="+91 98450 12345"
                value={formData.guardianPhone}
                onChange={(e) => handleChange('guardianPhone', e.target.value)}
              />
              <Input
                label="Guardian Email"
                type="email"
                placeholder="guardian@example.com"
                value={formData.guardianEmail}
                onChange={(e) => handleChange('guardianEmail', e.target.value)}
              />
              <div className="sm:col-span-2">
                <Input
                  label="Guardian Occupation / Workplace"
                  placeholder="e.g. Senior Civil Engineer, PWD"
                  value={formData.guardianOccupation}
                  onChange={(e) => handleChange('guardianOccupation', e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <Button variant="outline" size="sm" type="button" onClick={() => setActiveTab('academic')}>
                Previous
              </Button>
              <Button variant="primary" size="sm" type="button" onClick={() => setActiveTab('documents')}>
                Next: Documents Upload
              </Button>
            </div>
          </Card>
        )}

        {/* Tab 4: Documents Upload */}
        {activeTab === 'documents' && (
          <Card title="Verification Documents & Attachments">
            <div className="space-y-4">
              <div className="border-2 border-dashed border-outline-variant rounded-2xl p-8 text-center hover:border-primary transition-colors bg-surface-container-low/40 cursor-pointer">
                <UploadCloud className="w-10 h-10 text-primary mx-auto mb-2" />
                <h4 className="font-bold text-sm text-on-surface">Upload Verification Files</h4>
                <p className="text-xs text-on-surface-variant mt-1">
                  Drag and drop marksheets, ID proof (Aadhaar/Passport), or admission letter (PDF, PNG, JPG up to 10MB)
                </p>
                <div className="mt-4">
                  <Button variant="outline" size="sm" type="button">Browse Files</Button>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-3 bg-surface-container-low rounded-xl">
                  <div className="flex items-center gap-2.5">
                    <FileText className="w-4 h-4 text-primary" />
                    <span className="font-medium text-on-surface">12th_Standard_Transcript.pdf</span>
                  </div>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">Attached</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between mt-6 pt-4 border-t border-outline-variant/30">
              <Button variant="outline" size="sm" type="button" onClick={() => setActiveTab('guardian')}>
                Previous
              </Button>
              <Button
                variant="container"
                size="md"
                type="submit"
                icon={isSubmitting ? Loader2 : Save}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : isEdit ? 'Save Changes' : 'Complete Enrollment'}
              </Button>
            </div>
          </Card>
        )}
      </form>
    </div>
  );
}

export default StudentForm;

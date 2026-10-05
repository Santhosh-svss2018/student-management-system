import React, { useState } from 'react';
import {
  UserCheck,
  Mail,
  Phone,
  Building,
  MapPin,
  Calendar,
  Award,
  BookOpen,
  Shield,
  Clock,
  FileText,
  Key
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Tabs from '../../components/common/Tabs';
import ChangePasswordModal from '../../components/common/ChangePasswordModal';
import { useAuth } from '../../context/AuthContext';
import { MOCK_FACULTY, MOCK_COURSES } from '../../data/mockData';

export function TeacherProfile() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const { user, role } = useAuth();
  const isAdmin = role === 'admin';
  const faculty = MOCK_FACULTY[0];
  const displayName = user?.full_name || faculty.name;
  const displayEmail = user?.email || faculty.email;
  const avatarUrl = user?.full_name
    ? `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(user.full_name)}&backgroundColor=004494,0066cc,2563eb`
    : faculty.avatar;

  const tabs = [
    { id: 'overview', label: 'Faculty Overview', icon: UserCheck },
    { id: 'courses', label: 'Teaching Load & Courses', icon: BookOpen, count: 2 },
    { id: 'permissions', label: 'Access Control & Security', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* Profile Header Hero Card */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 sm:p-8 shadow-soft flex flex-col md:flex-row items-start md:items-center gap-6">
        <img
          src={avatarUrl}
          alt={displayName}
          className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl object-cover ring-4 ring-primary/20 shadow-card bg-primary/10"
        />

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-on-surface">
              {displayName}
            </h1>
            <Badge variant="primary" size="md">Faculty ID: {faculty.id}</Badge>
            <Badge variant="success" size="md">Active Staff</Badge>
          </div>

          <p className="text-sm font-semibold text-primary">
            {faculty.designation} • {faculty.department}
          </p>

          <div className="flex flex-wrap items-center gap-4 sm:gap-6 mt-4 text-xs text-on-surface-variant">
            <div className="flex items-center gap-1.5">
              <Mail className="w-4 h-4 text-on-surface-variant" />
              <span>{displayEmail}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Phone className="w-4 h-4 text-on-surface-variant" />
              <span>{faculty.phone}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-on-surface-variant" />
              <span>{faculty.cabin}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-2">
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
          <Button variant="outline" size="sm">Edit Profile</Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab Content: Overview */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8 space-y-6">
            <Card title="Academic Background & Research Specialization">
              <div className="space-y-4 text-xs sm:text-sm">
                <div>
                  <h4 className="font-bold text-on-surface">Primary Specialization</h4>
                  <p className="text-on-surface-variant mt-1 leading-relaxed">
                    {faculty.specialization}. Leading the Advanced Distributed Systems and High-Performance Cloud Lab in the Computer Science department.
                  </p>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-outline-variant/30">
                  <div className="p-3 bg-surface-container-low rounded-xl text-center">
                    <p className="text-xs text-on-surface-variant">Experience</p>
                    <p className="font-bold text-lg text-on-surface mt-0.5">{faculty.experience}</p>
                  </div>
                  <div className="p-3 bg-surface-container-low rounded-xl text-center">
                    <p className="text-xs text-on-surface-variant">Publications</p>
                    <p className="font-bold text-lg text-primary mt-0.5">{faculty.publications}</p>
                  </div>
                  <div className="p-3 bg-surface-container-low rounded-xl text-center">
                    <p className="text-xs text-on-surface-variant">Active Grants</p>
                    <p className="font-bold text-lg text-tertiary mt-0.5">{faculty.activeProjects}</p>
                  </div>
                  <div className="p-3 bg-surface-container-low rounded-xl text-center">
                    <p className="text-xs text-on-surface-variant">Joining Date</p>
                    <p className="font-bold text-sm text-on-surface mt-1">Aug 2016</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card title="Qualifications & Certifications">
              <div className="space-y-3 text-xs sm:text-sm">
                <div className="flex items-start gap-3 p-3 bg-surface-container-low/70 rounded-xl">
                  <Award className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-bold text-on-surface">Ph.D. in Computer Science & Engineering</h5>
                    <p className="text-on-surface-variant text-xs">Indian Institute of Science (IISc) Bengaluru • 2015</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-surface-container-low/70 rounded-xl">
                  <Award className="w-5 h-5 text-secondary flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-bold text-on-surface">M.Tech in Computer Networks</h5>
                    <p className="text-on-surface-variant text-xs">National Institute of Technology (NIT) • 2010</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-4 space-y-6">
            <Card title="Department Roles & Duties">
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
                  <p className="font-bold text-blue-900">Head of Curriculum Committee</p>
                  <p className="text-blue-700 mt-0.5">B.Tech CS 2024–2028 syllabus revision</p>
                </div>
                <div className="p-3 rounded-xl bg-purple-50 border border-purple-200">
                  <p className="font-bold text-purple-900">Faculty Advisor - 6th Sem CS-A</p>
                  <p className="text-purple-700 mt-0.5">Counseling and attendance mentorship</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Tab Content: Courses */}
      {activeTab === 'courses' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {MOCK_COURSES.slice(0, 2).map((c) => (
            <Card key={c.id} title={`${c.code}: ${c.title}`} subtitle={`${c.credits} Credits • Room: ${c.room}`}>
              <div className="space-y-3 text-xs sm:text-sm">
                <div className="flex justify-between py-1 border-b border-outline-variant/30">
                  <span className="text-on-surface-variant">Class Timings</span>
                  <span className="font-semibold text-on-surface">{c.schedule}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-outline-variant/30">
                  <span className="text-on-surface-variant">Enrolled Students</span>
                  <span className="font-semibold text-on-surface">{c.studentsCount} Students</span>
                </div>
                <div className="flex justify-between py-1 border-b border-outline-variant/30">
                  <span className="text-on-surface-variant">Class Average Attendance</span>
                  <span className="font-semibold text-tertiary">{c.attendance}%</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Tab Content: Permissions */}
      {activeTab === 'permissions' && (
        <Card title="Institutional Access & Permission Roles" subtitle="Role-Based Access Control (RBAC) settings for Faculty">
          <div className="space-y-4 text-xs sm:text-sm">
            {[
              { role: 'Take & Modify Daily Attendance', desc: 'Authorized for assigned CS-301 & CS-402 courses', status: 'Granted' },
              { role: 'Submit Midterm & Final Grades', desc: 'Permitted up to grade lock deadline', status: 'Granted' },
              { role: 'Institutional Report Generation', desc: 'Department-level aggregate view only', status: 'Granted' },
              { role: 'Student Enrollment / De-registration', desc: 'Requires Academic Registrar permission', status: 'Restricted' }
            ].map((p, i) => (
              <div key={i} className="flex items-center justify-between p-3.5 bg-surface-container-low rounded-xl">
                <div>
                  <p className="font-bold text-on-surface">{p.role}</p>
                  <p className="text-xs text-on-surface-variant mt-0.5">{p.desc}</p>
                </div>
                <Badge variant={p.status === 'Granted' ? 'success' : 'neutral'} size="sm">
                  {p.status}
                </Badge>
              </div>
            ))}

            {isAdmin && (
              <div className="pt-4 border-t border-outline-variant/40 flex items-center justify-between">
                <div>
                  <p className="font-bold text-sm text-on-surface">Faculty Authentication Credentials</p>
                  <p className="text-xs text-on-surface-variant">Admin password management for {displayName}</p>
                </div>
                <Button
                  variant="container"
                  size="sm"
                  icon={Key}
                  onClick={() => setIsPasswordModalOpen(true)}
                >
                  Change Password
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Admin Password Management Dialog */}
      {isAdmin && (
        <ChangePasswordModal
          isOpen={isPasswordModalOpen}
          onClose={() => setIsPasswordModalOpen(false)}
          targetUser={{
            full_name: displayName,
            email: displayEmail,
            role: 'teacher'
          }}
        />
      )}
    </div>
  );
}

export default TeacherProfile;

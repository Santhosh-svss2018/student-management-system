import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  Sparkles,
  ChevronDown,
  User,
  ShieldCheck,
  GraduationCap,
  Briefcase,
  LogOut,
  X,
  Check
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Badge from '../common/Badge';

export function Header({ onMenuClick }) {
  const { user, role, switchDevRole, logout } = useAuth();
  const navigate = useNavigate();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Attendance Alert', desc: 'CS-301 attendance fell below 75% for 2 students.', time: '10m ago', unread: true },
    { id: 2, title: 'Marks Submitted', desc: 'Prof. Marcus Vance uploaded Midterm Marks.', time: '1h ago', unread: true },
    { id: 3, title: 'Admissions Update', desc: 'Phase 2 enrollment opened for 2026 Batch.', time: '3h ago', unread: false }
  ]);

  const unreadCount = notifications.filter(n => n.unread).length;

  const handleRoleChange = (newRole) => {
    switchDevRole(newRole);
    if (newRole === 'admin') navigate('/admin');
    else if (newRole === 'teacher') navigate('/teacher');
    else if (newRole === 'student') navigate('/student-portal');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-surface-container-lowest/90 backdrop-blur-md border-b border-outline-variant/60 flex items-center justify-between px-4 sm:px-6">
      {/* Left section: Hamburger & Search */}
      <div className="flex items-center gap-3 md:gap-4 flex-1 max-w-xl">
        <button
          onClick={onMenuClick}
          className="p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div className="relative w-full max-w-md hidden sm:block">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            placeholder="Search students, courses, faculty, marks (Press ⌘K)..."
            className="w-full pl-9 pr-12 py-1.5 bg-surface-container-low border border-outline-variant/50 rounded-lg text-xs md:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
          />
          <div className="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none">
            <kbd className="px-1.5 py-0.5 text-[10px] font-semibold text-on-surface-variant bg-surface-container-highest rounded border border-outline-variant/50">
              ⌘K
            </kbd>
          </div>
        </div>
      </div>

      {/* Right section: Dev Role Switcher, Notifications & Profile */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* DEV ONLY ROLE PREVIEW TOOLBAR (Requirement 4) */}
        <div className="hidden md:flex items-center gap-1 bg-surface-container px-2 py-1 rounded-xl border border-outline-variant/60 text-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant px-1 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Role Preview:
          </span>
          <button
            onClick={() => handleRoleChange('admin')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              role === 'admin'
                ? 'bg-primary text-white shadow-xs font-semibold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
            }`}
          >
            Admin
          </button>
          <button
            onClick={() => handleRoleChange('teacher')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              role === 'teacher'
                ? 'bg-primary text-white shadow-xs font-semibold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
            }`}
          >
            Teacher
          </button>
          <button
            onClick={() => handleRoleChange('student')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              role === 'student'
                ? 'bg-primary text-white shadow-xs font-semibold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
            }`}
          >
            Student
          </button>
        </div>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfileMenu(false);
            }}
            className="relative p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg transition-colors"
            aria-label="View notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-error rounded-full ring-2 ring-white animate-pulse" />
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-elevated z-50 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant/40 bg-surface-container-low">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-sm text-on-surface">Notifications</h4>
                  {unreadCount > 0 && (
                    <Badge variant="primary" size="sm">{unreadCount} New</Badge>
                  )}
                </div>
                <button
                  onClick={() => setNotifications(notifications.map(n => ({ ...n, unread: false })))}
                  className="text-xs text-primary hover:underline font-medium"
                >
                  Mark all as read
                </button>
              </div>
              <div className="max-h-72 overflow-y-auto divide-y divide-outline-variant/20">
                {notifications.map((n) => (
                  <div key={n.id} className={`p-3.5 hover:bg-surface-container transition-colors ${n.unread ? 'bg-primary/5' : ''}`}>
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-semibold text-on-surface">{n.title}</p>
                      <span className="text-[10px] text-on-surface-variant">{n.time}</span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1">{n.desc}</p>
                  </div>
                ))}
              </div>
              <div className="p-2 border-t border-outline-variant/40 text-center bg-surface-container-low">
                <button
                  onClick={() => setShowNotifications(false)}
                  className="text-xs text-primary font-medium hover:underline"
                >
                  Close notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Menu */}
        <div className="relative">
          <button
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2.5 p-1 pl-1.5 rounded-xl hover:bg-surface-container transition-colors"
          >
            <img
              src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
              alt={user?.name || 'User Avatar'}
              className="w-8 h-8 rounded-full object-cover ring-2 ring-primary/20"
            />
            <div className="hidden sm:block text-left">
              <p className="text-xs font-bold text-on-surface leading-none">{user?.name || 'Academic User'}</p>
              <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mt-0.5">
                {role}
              </p>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-on-surface-variant hidden sm:block" />
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-64 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-elevated z-50 overflow-hidden">
              <div className="p-4 border-b border-outline-variant/40 bg-surface-container-low">
                <p className="text-sm font-bold text-on-surface">{user?.name}</p>
                <p className="text-xs text-on-surface-variant truncate">{user?.email}</p>
                <div className="mt-2">
                  <Badge variant="primary" size="sm" className="capitalize">{role} Account</Badge>
                </div>
              </div>

              {/* Mobile dev role switcher in menu */}
              <div className="p-3 border-b border-outline-variant/30 md:hidden bg-slate-50">
                <p className="text-[10px] font-bold uppercase text-on-surface-variant mb-1.5">Dev Preview Role:</p>
                <div className="flex gap-1">
                  {['admin', 'teacher', 'student'].map((r) => (
                    <button
                      key={r}
                      onClick={() => handleRoleChange(r)}
                      className={`flex-1 py-1 text-xs rounded capitalize font-medium ${role === r ? 'bg-primary text-white' : 'bg-surface-container text-on-surface'}`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              <div className="py-1 text-xs">
                <button
                  onClick={() => {
                    setShowProfileMenu(false);
                    if (role === 'teacher') navigate('/teacher/profile');
                    else if (role === 'student') navigate('/student-portal');
                    else navigate('/admin');
                  }}
                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-on-surface hover:bg-surface-container transition-colors"
                >
                  <User className="w-4 h-4 text-on-surface-variant" />
                  <span>My Profile Details</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-error hover:bg-red-50 transition-colors border-t border-outline-variant/20"
                >
                  <LogOut className="w-4 h-4 text-error" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;

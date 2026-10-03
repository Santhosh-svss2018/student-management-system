import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  UserPlus,
  CalendarCheck,
  Award,
  FileBarChart2,
  Bot,
  Sparkles,
  UserCheck,
  Palette,
  LogOut,
  ChevronRight,
  GraduationCap
} from 'lucide-react';
import EduManageLogo from '../../assets/EduManageLogo';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ isOpen, onClose }) {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navGroups = [
    {
      group: 'Portals',
      items: [
        { label: 'Admin Dashboard', path: '/admin', icon: LayoutDashboard, roles: ['admin'] },
        { label: 'Faculty Dashboard', path: '/teacher', icon: LayoutDashboard, roles: ['teacher', 'admin'] },
        { label: 'Student Portal', path: '/student-portal', icon: GraduationCap, roles: ['student', 'admin'] },
      ]
    },
    {
      group: 'Academic Operations',
      items: [
        { label: 'Student Directory', path: '/students', icon: Users, roles: ['admin', 'teacher'] },
        { label: 'Add New Student', path: '/students/new', icon: UserPlus, roles: ['admin'] },
        { label: 'Mark Attendance', path: '/teacher/attendance', icon: CalendarCheck, roles: ['teacher', 'admin'] },
        { label: 'Marks & Grading', path: '/teacher/marks', icon: Award, roles: ['teacher', 'admin'] },
        { label: 'Faculty Profile', path: '/teacher/profile', icon: UserCheck, roles: ['teacher', 'admin'] },
      ]
    },
    {
      group: 'Intelligence & Reports',
      items: [
        { label: 'AI Risk Insights', path: '/ai/insights', icon: Sparkles, roles: ['admin', 'teacher'], badge: 'AI' },
        { label: 'EduAI Assistant', path: '/student-portal/ai', icon: Bot, roles: ['student', 'admin', 'teacher'], badge: 'Beta' },
        { label: 'Reports & Analytics', path: '/admin/reports', icon: FileBarChart2, roles: ['admin'] },
      ]
    },
    {
      group: 'System & Tools',
      items: [
        { label: 'UI Styleguide Shell', path: '/styleguide', icon: Palette, roles: ['admin', 'teacher', 'student'] },
      ]
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 left-0 bottom-0 z-40 w-64 bg-surface-container-lowest border-r border-outline-variant/60 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center border-b border-outline-variant/40">
          <EduManageLogo />
        </div>

        {/* Navigation List */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {navGroups.map((group, groupIdx) => {
            const filteredItems = group.items.filter((item) => item.roles.includes(role));
            if (filteredItems.length === 0) return null;

            return (
              <div key={groupIdx}>
                <div className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-on-surface-variant/80 font-sans">
                  {group.group}
                </div>
                <nav className="space-y-1">
                  {filteredItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/admin' || item.path === '/teacher' || item.path === '/student-portal'}
                        onClick={() => {
                          if (window.innerWidth < 1024) onClose?.();
                        }}
                        className={({ isActive }) =>
                          `flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 group select-none ${
                            isActive
                              ? 'bg-primary-container text-white shadow-xs font-semibold'
                              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                          }`
                        }
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-105" />
                          <span>{item.label}</span>
                        </div>
                        {item.badge && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase rounded-full bg-[#6ffbbe] text-[#002113]">
                            {item.badge}
                          </span>
                        )}
                      </NavLink>
                    );
                  })}
                </nav>
              </div>
            );
          })}
        </div>

        {/* User Footer Profile & Logout */}
        <div className="p-3 border-t border-outline-variant/40 bg-surface-container-low/50">
          <div className="flex items-center gap-3 p-2 rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-xs">
            <img
              src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
              alt={user?.name || 'User'}
              className="w-9 h-9 rounded-full object-cover ring-1 ring-primary/20"
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-on-surface truncate">{user?.name || 'Academic User'}</p>
              <p className="text-[11px] text-on-surface-variant uppercase tracking-wider font-semibold capitalize truncate">
                {user?.role || role}
              </p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="p-1.5 text-on-surface-variant hover:text-error hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const ROUTE_NAME_MAP = {
  admin: 'Admin Portal',
  teacher: 'Faculty Portal',
  'student-portal': 'Student Portal',
  students: 'Students',
  new: 'Add Student',
  edit: 'Edit Details',
  attendance: 'Attendance Management',
  marks: 'Marks & Grading',
  profile: 'Faculty Profile',
  reports: 'Institutional Reports',
  'ai-insights': 'AI Risk Insights',
  insights: 'AI Insights',
  ai: 'EduAI Assistant',
  styleguide: 'Design System Shell'
};

export function Breadcrumbs({ className = '' }) {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (pathnames.length === 0 || pathnames[0] === 'login') return null;

  return (
    <nav className={`flex items-center text-xs text-on-surface-variant mb-4 ${className}`} aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1.5 md:space-x-2">
        <li className="inline-flex items-center">
          <Link to="/" className="inline-flex items-center text-on-surface-variant hover:text-primary transition-colors">
            <Home className="w-3.5 h-3.5 mr-1" />
            <span>Home</span>
          </Link>
        </li>
        {pathnames.map((value, index) => {
          const to = `/${pathnames.slice(0, index + 1).join('/')}`;
          const isLast = index === pathnames.length - 1;
          const displayName = ROUTE_NAME_MAP[value] || (value.startsWith('STU-') ? 'Student Profile' : value);

          return (
            <li key={to} className="inline-flex items-center">
              <ChevronRight className="w-3.5 h-3.5 text-outline-variant" />
              {isLast ? (
                <span className="ml-1.5 md:ml-2 font-semibold text-on-surface capitalize">
                  {displayName}
                </span>
              ) : (
                <Link
                  to={to}
                  className="ml-1.5 md:ml-2 text-on-surface-variant hover:text-primary transition-colors capitalize"
                >
                  {displayName}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default Breadcrumbs;

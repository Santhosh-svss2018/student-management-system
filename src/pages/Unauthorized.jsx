import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext';

export function Unauthorized() {
  const navigate = useNavigate();
  const { role } = useAuth();

  const handleGoHome = () => {
    if (role === 'admin') navigate('/admin');
    else if (role === 'teacher') navigate('/teacher');
    else if (role === 'student') navigate('/student-portal');
    else navigate('/login');
  };

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 bg-red-100 text-error rounded-2xl flex items-center justify-center mb-4 ring-8 ring-red-50">
        <ShieldAlert className="w-8 h-8" />
      </div>
      <h1 className="font-display text-2xl md:text-3xl font-bold text-on-surface">403 - Access Restricted</h1>
      <p className="text-sm text-on-surface-variant max-w-md mt-2">
        Your current role (<span className="font-semibold capitalize text-on-surface">{role}</span>) does not have authorization to view this module.
      </p>
      <div className="flex items-center gap-3 mt-6">
        <Button variant="outline" onClick={() => navigate(-1)} icon={ArrowLeft}>
          Go Back
        </Button>
        <Button variant="primary" onClick={handleGoHome} icon={Home}>
          Return to Portal
        </Button>
      </div>
    </div>
  );
}

export default Unauthorized;

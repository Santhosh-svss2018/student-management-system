import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileQuestion, ArrowLeft, Home } from 'lucide-react';
import Button from '../components/common/Button';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 bg-blue-50 text-primary rounded-2xl flex items-center justify-center mb-4 ring-8 ring-blue-50/50">
        <FileQuestion className="w-8 h-8" />
      </div>
      <h1 className="font-display text-2xl md:text-3xl font-bold text-on-surface">404 - Page Not Found</h1>
      <p className="text-sm text-on-surface-variant max-w-md mt-2">
        The screen or academic record you are looking for does not exist or has been relocated.
      </p>
      <div className="flex items-center gap-3 mt-6">
        <Button variant="outline" onClick={() => navigate(-1)} icon={ArrowLeft}>
          Go Back
        </Button>
        <Button variant="primary" onClick={() => navigate('/')} icon={Home}>
          Home
        </Button>
      </div>
    </div>
  );
}

export default NotFound;

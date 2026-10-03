import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  GraduationCap,
  Users,
  Building2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import EduManageLogo from '../../assets/EduManageLogo';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import { useAuth } from '../../context/AuthContext';

export function SignInPage() {
  const { login, isAuthenticated, user, authError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [selectedRole, setSelectedRole] = useState('admin');
  const [email, setEmail] = useState('sarah.jenkins@edumanage.edu');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const rolePresets = {
    admin: {
      email: 'sarah.jenkins@edumanage.edu',
      label: 'Administrator',
      icon: Building2,
      target: '/admin',
      desc: 'System oversight, admissions, institution reports'
    },
    teacher: {
      email: 'marcus.vance@edumanage.edu',
      label: 'Faculty / Teacher',
      icon: Users,
      target: '/teacher',
      desc: 'Attendance tracking, marks entry, course rosters'
    },
    student: {
      email: 'arun.kumar@student.edumanage.edu',
      label: 'Student Portal',
      icon: GraduationCap,
      target: '/student-portal',
      desc: 'Academic progress, timetable, grades & AI tutor'
    }
  };

  // If already authenticated, redirect to appropriate portal
  useEffect(() => {
    if (isAuthenticated && user) {
      const from = location.state?.from?.pathname;
      if (from && from !== '/login') {
        navigate(from, { replace: true });
      } else if (user.role === 'admin') {
        navigate('/admin', { replace: true });
      } else if (user.role === 'teacher') {
        navigate('/teacher', { replace: true });
      } else if (user.role === 'student') {
        navigate('/student-portal', { replace: true });
      } else {
        navigate('/admin', { replace: true });
      }
    }
  }, [isAuthenticated, user, navigate, location]);

  const handleRoleSelect = (roleKey) => {
    setSelectedRole(roleKey);
    setEmail(rolePresets[roleKey].email);
    setErrorMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsSubmitting(true);

    try {
      const authenticatedUser = await login(email, password);

      const from = location.state?.from?.pathname;
      if (from && from !== '/login') {
        navigate(from, { replace: true });
        return;
      }

      const roleKey = authenticatedUser.role;
      const targetPath = rolePresets[roleKey]?.target || (
        roleKey === 'teacher' ? '/teacher' : roleKey === 'student' ? '/student-portal' : '/admin'
      );
      navigate(targetPath, { replace: true });
    } catch (err) {
      setErrorMessage(err.message || 'Authentication failed. Please verify your email and password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayError = errorMessage || authError;

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background ambient gradient highlights */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-tertiary-fixed-dim/20 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-4xl px-4 relative z-10">
        <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl shadow-elevated overflow-hidden grid grid-cols-1 lg:grid-cols-12">
          {/* Left Hero & Value Proposition Section */}
          <div className="lg:col-span-5 bg-gradient-to-br from-primary via-[#003da8] to-[#002670] p-8 text-white flex flex-col justify-between relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-400/20 via-transparent to-transparent pointer-events-none" />

            <div className="relative z-10">
              <EduManageLogo showText={true} textClassName="text-white" />
              <div className="mt-8">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-white border border-white/20">
                  <Sparkles className="w-3.5 h-3.5 text-tertiary-fixed" />
                  Institutional Suite 2.0
                </span>
                <h2 className="font-display text-2xl sm:text-3xl font-bold tracking-tight mt-4 leading-snug">
                  Manage your university with modern clarity.
                </h2>
                <p className="text-xs sm:text-sm text-blue-100/90 mt-3 leading-relaxed">
                  Unified student management, attendance rosters, automated grade calculation, and proactive AI risk insights.
                </p>
              </div>

              {/* Feature Points */}
              <div className="mt-8 space-y-3.5">
                {[
                  'Unified Academic & Student Directory',
                  'Instant Attendance & Grade Evaluation',
                  'AI-Powered Early Dropout Risk Alerts'
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-2.5 text-xs text-blue-50 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-tertiary-fixed flex-shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-white/15 relative z-10">
              <div className="flex items-center gap-2 text-xs text-blue-200">
                <ShieldCheck className="w-4 h-4 text-emerald-300" />
                <span>256-bit Institutional TLS Encryption</span>
              </div>
            </div>
          </div>

          {/* Right Login Form Section */}
          <div className="lg:col-span-7 p-8 sm:p-10 flex flex-col justify-center">
            <div>
              <h3 className="font-display text-2xl font-bold text-on-surface">Welcome Back</h3>
              <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
                Select your academic portal to sign in to EduManage.
              </p>
            </div>

            {/* Error Banner */}
            {displayError && (
              <div className="mt-4 p-3.5 bg-red-50/90 border border-red-200 rounded-xl flex items-start gap-2.5 text-red-800 text-xs animate-in fade-in duration-200">
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold">Sign in failed</p>
                  <p className="mt-0.5 text-red-700">{displayError}</p>
                </div>
              </div>
            )}

            {/* Role Selection Tabs */}
            <div className="mt-6">
              <label className="block text-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-2">
                Select Portal / Role
              </label>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(rolePresets).map(([key, config]) => {
                  const Icon = config.icon;
                  const isSelected = selectedRole === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => handleRoleSelect(key)}
                      className={`p-3 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
                        isSelected
                          ? 'border-primary bg-primary/5 ring-2 ring-primary/20 shadow-xs'
                          : 'border-outline-variant/60 hover:border-outline bg-white'
                      }`}
                    >
                      <Icon className={`w-5 h-5 ${isSelected ? 'text-primary' : 'text-on-surface-variant'}`} />
                      <div className="mt-2">
                        <p className={`text-xs font-bold leading-tight ${isSelected ? 'text-primary' : 'text-on-surface'}`}>
                          {config.label}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <Input
                label="Institutional Email / ID"
                type="email"
                icon={Mail}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@university.edu"
                disabled={isSubmitting}
              />

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold text-on-surface">Password</label>
                  <button type="button" className="text-xs text-primary hover:underline font-medium">
                    Forgot password?
                  </button>
                </div>
                <Input
                  type="password"
                  icon={Lock}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your secure password"
                  disabled={isSubmitting}
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary"
                    disabled={isSubmitting}
                  />
                  <span className="text-xs text-on-surface-variant font-medium">Keep me signed in</span>
                </label>
              </div>

              <Button
                type="submit"
                variant="container"
                size="lg"
                className="w-full mt-4"
                icon={isSubmitting ? Loader2 : ArrowRight}
                iconPosition="right"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing in...' : `Sign In to ${rolePresets[selectedRole].label}`}
              </Button>
            </form>

            <div className="mt-6 pt-4 border-t border-outline-variant/40 text-center">
              <p className="text-xs text-on-surface-variant">
                Need technical assistance?{' '}
                <a href="#support" className="text-primary font-semibold hover:underline">
                  Contact IT Helpdesk
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignInPage;

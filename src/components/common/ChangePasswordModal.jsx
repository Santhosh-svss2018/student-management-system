import React, { useState, useEffect } from 'react';
import {
  Key,
  Lock,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import Badge from './Badge';
import { userService } from '../../services/userService';

/**
 * Admin-Only Change Password Modal Dialog
 * Allows administrators to securely update passwords for Students or Faculty/Teachers.
 */
export function ChangePasswordModal({
  isOpen,
  onClose,
  targetUser,
  onSuccess
}) {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Reset form state when modal opens or target changes
  useEffect(() => {
    if (isOpen) {
      setNewPassword('');
      setConfirmPassword('');
      setShowNewPassword(false);
      setShowConfirmPassword(false);
      setErrorMessage(null);
      setSuccessMessage(null);
      setIsSubmitting(false);
    }
  }, [isOpen, targetUser]);

  if (!isOpen || !targetUser) return null;

  const targetName = targetUser.full_name || targetUser.name || 'User Account';
  const targetEmail = targetUser.email || '';
  const targetId = targetUser.student_id || targetUser.id || targetUser._id || targetEmail;
  const roleType = (targetUser.role || (targetUser.student_id ? 'student' : 'faculty')).toLowerCase();
  const isStudent = roleType === 'student';

  const roleBadgeVariant = isStudent ? 'primary' : 'tertiary';
  const roleTitle = isStudent ? 'Student' : 'Faculty / Teacher';

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    // Frontend validation
    if (!newPassword) {
      setErrorMessage('New password is required.');
      return;
    }
    if (newPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }
    if (!confirmPassword) {
      setErrorMessage('Please confirm the new password.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      return;
    }

    setIsSubmitting(true);

    try {
      // Identifier can be user ID, student ID, or email
      const identifier = targetUser.id || targetUser._id || targetUser.student_id || targetEmail;
      await userService.changeUserPassword(identifier, newPassword);

      setSuccessMessage(`Password for ${targetName} has been successfully updated.`);
      if (onSuccess) onSuccess();

      // Clear password fields
      setNewPassword('');
      setConfirmPassword('');

      // Auto-close modal after brief visual confirmation
      setTimeout(() => {
        onClose();
      }, 1600);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to update user password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isPasswordValid = newPassword.length >= 8;
  const doPasswordsMatch = newPassword && confirmPassword && newPassword === confirmPassword;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isStudent ? 'Change Student Password' : 'Change Faculty Password'}
      subtitle="Admin Authentication & Password Management"
      maxWidth="max-w-md"
    >
      <div className="space-y-5">
        {/* Target User Summary Card */}
        <div className="flex items-center gap-3 p-3.5 bg-surface-container-low rounded-xl border border-outline-variant/50">
          <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center flex-shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-bold text-sm text-on-surface truncate">{targetName}</p>
              <Badge variant={roleBadgeVariant} size="sm">{roleTitle}</Badge>
            </div>
            <p className="text-xs text-on-surface-variant truncate">{targetEmail}</p>
            {targetUser.student_id && (
              <p className="text-[11px] font-mono text-primary mt-0.5">ID: {targetUser.student_id}</p>
            )}
          </div>
        </div>

        {/* Success Alert Banner */}
        {successMessage && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-2.5 text-emerald-900 text-xs animate-in fade-in duration-150">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Password Updated Successfully</p>
              <p className="text-emerald-700 mt-0.5">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Error Alert Banner */}
        {errorMessage && (
          <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2.5 text-red-900 text-xs animate-in fade-in duration-150">
            <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Error Updating Password</p>
              <p className="text-red-700 mt-0.5">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Form Inputs */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* New Password */}
          <div>
            <label className="block text-xs font-semibold text-on-surface mb-1.5">
              New Password <span className="text-error">*</span>
            </label>
            <div className="relative rounded-lg">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type={showNewPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="Enter minimum 8 characters"
                disabled={isSubmitting}
                className="w-full bg-white border border-outline-variant hover:border-outline focus:border-primary rounded-lg text-sm text-on-surface placeholder:text-on-surface-variant/60 py-2 pl-9 pr-10 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-on-surface-variant hover:text-on-surface"
              >
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-xs font-semibold text-on-surface mb-1.5">
              Confirm New Password <span className="text-error">*</span>
            </label>
            <div className="relative rounded-lg">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
                <Key className="w-4 h-4" />
              </div>
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="Re-type new password"
                disabled={isSubmitting}
                className="w-full bg-white border border-outline-variant hover:border-outline focus:border-primary rounded-lg text-sm text-on-surface placeholder:text-on-surface-variant/60 py-2 pl-9 pr-10 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-on-surface-variant hover:text-on-surface"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Security Rules Checklist */}
          <div className="p-3 bg-surface-container-low/60 rounded-xl space-y-1.5 text-xs text-on-surface-variant">
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${isPasswordValid ? 'bg-emerald-500' : 'bg-slate-300'}`} />
              <span className={isPasswordValid ? 'text-emerald-700 font-medium' : ''}>
                Minimum 8 characters length
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${doPasswordsMatch ? 'bg-emerald-500' : 'bg-slate-300'}`} />
              <span className={doPasswordsMatch ? 'text-emerald-700 font-medium' : ''}>
                Passwords match
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="container"
              size="sm"
              icon={isSubmitting ? Loader2 : ShieldCheck}
              disabled={isSubmitting || !isPasswordValid || !doPasswordsMatch}
            >
              {isSubmitting ? 'Updating...' : 'Set Password'}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}

export default ChangePasswordModal;

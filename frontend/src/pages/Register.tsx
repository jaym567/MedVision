// frontend/src/pages/Register.tsx
/**
 * Registration page for new user accounts
 */

import { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useRegister } from '@/hooks/useAuth';
import FormInput from '@/components/FormInput';
import FormButton from '@/components/FormButton';
import SafetyNotice from '@/components/SafetyNotice';
import { UserRole } from '@/types/user';
import { isValidEmail, validatePassword } from '@/utils/validation';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: UserRole.PHYSICIAN,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const registerMutation = useRegister();

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) {
        newErrors.password = passwordValidation.message || 'Invalid password';
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Full name validation
    if (!formData.fullName) {
      newErrors.fullName = 'Full name is required';
    } else if (formData.fullName.trim().length < 2) {
      newErrors.fullName = 'Please enter your full name';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    registerMutation.mutate({
      email: formData.email.toLowerCase().trim(),
      password: formData.password,
      full_name: formData.fullName.trim(),
      role: formData.role,
    });
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">
            MedVision AI
          </h1>
          <p className="text-gray-400">
            Create Your Account
          </p>
        </div>

        {/* Safety Notice */}
        <SafetyNotice />

        {/* Registration Form */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
          <h2 className="text-2xl font-semibold text-white mb-6">
            Register
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <FormInput
              label="Full Name"
              type="text"
              value={formData.fullName}
              onChange={(e) => handleChange('fullName', e.target.value)}
              error={errors.fullName}
              placeholder="Dr. Jane Smith"
              required
              disabled={registerMutation.isPending}
              autoComplete="name"
            />

            <FormInput
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              error={errors.email}
              placeholder="dr.smith@hospital.com"
              required
              disabled={registerMutation.isPending}
              autoComplete="email"
            />

            <FormInput
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              error={errors.password}
              placeholder="Minimum 8 characters"
              helperText="At least 8 characters"
              required
              disabled={registerMutation.isPending}
              autoComplete="new-password"
            />

            <FormInput
              label="Confirm Password"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => handleChange('confirmPassword', e.target.value)}
              error={errors.confirmPassword}
              placeholder="Re-enter your password"
              required
              disabled={registerMutation.isPending}
              autoComplete="new-password"
            />

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Role <span className="text-red-400">*</span>
              </label>
              <select
                value={formData.role}
                onChange={(e) => handleChange('role', e.target.value)}
                disabled={registerMutation.isPending}
                className="
                  w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                  text-white
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors
                "
                required
              >
                <option value={UserRole.PHYSICIAN}>Physician</option>
                <option value={UserRole.RESEARCHER}>Researcher</option>
                <option value={UserRole.ADMIN}>Administrator</option>
              </select>
              <p className="mt-1 text-sm text-gray-500">
                Select your professional role
              </p>
            </div>

            <FormButton
              type="submit"
              variant="primary"
              fullWidth
              isLoading={registerMutation.isPending}
            >
              Create Account
            </FormButton>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-blue-400 hover:text-blue-300 font-medium"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          <p>Sprint 3: Secure Frontend Study Workstation</p>
        </div>
      </div>
    </div>
  );
}

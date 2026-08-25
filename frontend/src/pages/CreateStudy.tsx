// frontend/src/pages/CreateStudy.tsx
import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useCreateStudy } from '../hooks/useCreateStudy';
import { StudyModality, StudyCreateRequest } from '../types/study';
import FormInput from '../components/FormInput';
import FormButton from '../components/FormButton';
import SafetyNotice from '../components/SafetyNotice';
import { isValidMRN, validateJSON, isDateNotFuture } from '../utils/validation';
import { getTodayISO } from '../utils/date';
import { formatModality } from '../utils/formatting';

interface FormData {
  // Patient fields
  mrn: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  sex: 'M' | 'F' | 'O';
  medicalHistory: string;
  // Study fields
  modality: StudyModality | '';
  bodyPart: string;
  description: string;
  studyDate: string;
  accessionNumber: string;
  metadata: string;
}

interface FormErrors {
  [key: string]: string;
}

const CreateStudy: React.FC = () => {
  const navigate = useNavigate();
  const { mutate: createStudy, isPending } = useCreateStudy();

  const [formData, setFormData] = useState<FormData>({
    mrn: '',
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    sex: 'M',
    medicalHistory: '',
    modality: '',
    bodyPart: '',
    description: '',
    studyDate: getTodayISO(),
    accessionNumber: '',
    metadata: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Patient validation
    if (!formData.mrn.trim()) {
      newErrors.mrn = 'MRN is required';
    } else if (!isValidMRN(formData.mrn)) {
      newErrors.mrn = 'MRN must be alphanumeric';
    }

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    } else if (formData.firstName.trim().length < 2) {
      newErrors.firstName = 'First name must be at least 2 characters';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    } else if (formData.lastName.trim().length < 2) {
      newErrors.lastName = 'Last name must be at least 2 characters';
    }

    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    } else if (isDateNotFuture(formData.dateOfBirth) === false) {
      newErrors.dateOfBirth = 'Date of birth cannot be in the future';
    }

    // Study validation
    if (!formData.modality) {
      newErrors.modality = 'Modality is required';
    }

    if (!formData.studyDate) {
      newErrors.studyDate = 'Study date is required';
    } else if (isDateNotFuture(formData.studyDate) === false) {
      newErrors.studyDate = 'Study date cannot be in the future';
    }

    // Metadata JSON validation (optional field)
    if (formData.metadata.trim() && !validateJSON(formData.metadata)) {
      newErrors.metadata = 'Invalid JSON format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Parse metadata if provided
    let metadata: Record<string, any> | undefined;
    if (formData.metadata.trim()) {
      try {
        metadata = JSON.parse(formData.metadata);
      } catch {
        setErrors((prev) => ({ ...prev, metadata: 'Invalid JSON format' }));
        return;
      }
    }

    const requestData: StudyCreateRequest = {
      patient: {
        mrn: formData.mrn.trim(),
        first_name: formData.firstName.trim(),
        last_name: formData.lastName.trim(),
        date_of_birth: formData.dateOfBirth,
        sex: formData.sex,
        medical_history: formData.medicalHistory.trim() || undefined,
      },
      study: {
        modality: formData.modality as StudyModality,
        body_part_examined: formData.bodyPart.trim() || undefined,
        study_description: formData.description.trim() || undefined,
        study_date: formData.studyDate,
        accession_number: formData.accessionNumber.trim() || undefined,
        metadata,
      },
    };

    createStudy(requestData);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/studies')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft size={18} />
          Back to Studies
        </button>
        <h1 className="text-2xl font-bold text-white">Create New Study</h1>
        <p className="text-gray-400 mt-1">
          Enter patient and study information to create a new imaging study
        </p>
      </div>

      {/* Safety Notice */}
      <SafetyNotice />

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Patient Information Section */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Patient Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              label="Medical Record Number (MRN)"
              name="mrn"
              value={formData.mrn}
              onChange={handleChange}
              error={errors.mrn}
              required
              placeholder="e.g., MRN123456"
              disabled={isPending}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormInput
                label="First Name"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                error={errors.firstName}
                required
                placeholder="John"
                disabled={isPending}
              />

              <FormInput
                label="Last Name"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                error={errors.lastName}
                required
                placeholder="Doe"
                disabled={isPending}
              />
            </div>

            <FormInput
              label="Date of Birth"
              name="dateOfBirth"
              type="date"
              value={formData.dateOfBirth}
              onChange={handleChange}
              error={errors.dateOfBirth}
              required
              disabled={isPending}
            />

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Sex <span className="text-red-500">*</span>
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleChange}
                disabled={isPending}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Medical History
              </label>
              <textarea
                name="medicalHistory"
                value={formData.medicalHistory}
                onChange={handleChange}
                disabled={isPending}
                rows={3}
                placeholder="Enter relevant medical history (optional)"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>
          </div>
        </div>

        {/* Study Information Section */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Study Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Modality <span className="text-red-500">*</span>
              </label>
              <select
                name="modality"
                value={formData.modality}
                onChange={handleChange}
                disabled={isPending}
                className={`w-full px-3 py-2 bg-gray-900 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 ${
                  errors.modality ? 'border-red-500' : 'border-gray-700'
                }`}
              >
                <option value="">Select modality...</option>
                {Object.values(StudyModality).map((modality) => (
                  <option key={modality} value={modality}>
                    {formatModality(modality)}
                  </option>
                ))}
              </select>
              {errors.modality && (
                <p className="mt-1 text-sm text-red-500">{errors.modality}</p>
              )}
            </div>

            <FormInput
              label="Body Part Examined"
              name="bodyPart"
              value={formData.bodyPart}
              onChange={handleChange}
              placeholder="e.g., Chest, Abdomen, Head"
              disabled={isPending}
            />

            <FormInput
              label="Study Date"
              name="studyDate"
              type="date"
              value={formData.studyDate}
              onChange={handleChange}
              error={errors.studyDate}
              required
              disabled={isPending}
            />

            <FormInput
              label="Accession Number"
              name="accessionNumber"
              value={formData.accessionNumber}
              onChange={handleChange}
              placeholder="e.g., ACC2024001"
              disabled={isPending}
            />

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Study Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                disabled={isPending}
                rows={2}
                placeholder="Enter study description (optional)"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Metadata (JSON)
              </label>
              <textarea
                name="metadata"
                value={formData.metadata}
                onChange={handleChange}
                disabled={isPending}
                rows={4}
                placeholder='{"key": "value"}'
                className={`w-full px-3 py-2 bg-gray-900 border rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 font-mono text-sm ${
                  errors.metadata ? 'border-red-500' : 'border-gray-700'
                }`}
              />
              {errors.metadata && (
                <p className="mt-1 text-sm text-red-500">{errors.metadata}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Optional: Enter valid JSON for additional metadata
              </p>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex gap-4">
          <FormButton
            type="button"
            variant="secondary"
            onClick={() => navigate('/studies')}
            disabled={isPending}
          >
            Cancel
          </FormButton>
          <FormButton
            type="submit"
            variant="primary"
            isLoading={isPending}
            fullWidth
          >
            Create Study
          </FormButton>
        </div>
      </form>
    </div>
  );
};

export default CreateStudy;

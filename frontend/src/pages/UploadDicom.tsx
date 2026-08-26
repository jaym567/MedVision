// frontend/src/pages/UploadDicom.tsx

import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUploadDicom } from '../hooks/useUploadDicom';
import { SafetyNotice } from '../components/SafetyNotice';
import { FormButton } from '../components/FormButton';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const UploadDicom: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const uploadMutation = useUploadDicom();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleCancel = () => {
    navigate('/studies');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-100">Upload DICOM File</h1>
        <p className="text-gray-400 mt-2">
          Upload a DICOM file to create a new study
        </p>
      </div>

      <SafetyNotice className="mb-6">
        Use only synthetic or properly de-identified DICOM files. Never upload
        files containing real patient health information (PHI).
      </SafetyNotice>

      <div className="bg-gray-800 rounded-lg shadow-xl p-8">
        {uploadMutation.isPending ? (
          <div className="flex flex-col items-center justify-center py-12">
            <LoadingSpinner size="large" />
            <p className="text-gray-300 mt-4">Uploading and processing...</p>
            {selectedFile && (
              <p className="text-gray-500 text-sm mt-2">
                {selectedFile.name} ({formatFileSize(selectedFile.size)})
              </p>
            )}
          </div>
        ) : (
          <>
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragging
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-600 hover:border-gray-500'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".dcm,application/dicom"
                onChange={handleFileSelect}
                className="hidden"
              />

              {selectedFile ? (
                <div className="space-y-4">
                  <div className="text-6xl">📁</div>
                  <div>
                    <p className="text-lg font-medium text-gray-200">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-sm text-blue-400 hover:text-blue-300 underline"
                  >
                    Choose different file
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-6xl">📂</div>
                  <div>
                    <p className="text-lg text-gray-300 mb-2">
                      Drag and drop a DICOM file here
                    </p>
                    <p className="text-sm text-gray-500 mb-4">or</p>
                    <button
                      onClick={handleBrowseClick}
                      className="text-blue-400 hover:text-blue-300 font-medium underline"
                    >
                      Browse files
                    </button>
                  </div>
                  <p className="text-xs text-gray-600 mt-4">
                    Supported: .dcm files (max 100 MB)
                  </p>
                </div>
              )}
            </div>

            {uploadMutation.isError && (
              <div className="mt-6 p-4 bg-red-900/20 border border-red-800 rounded-lg">
                <p className="text-red-400 text-sm">
                  {uploadMutation.error?.response?.data?.detail ||
                    uploadMutation.error?.message ||
                    'Upload failed. Please try again.'}
                </p>
              </div>
            )}

            <div className="flex gap-4 mt-8">
              <FormButton
                onClick={handleUpload}
                disabled={!selectedFile || uploadMutation.isPending}
                className="flex-1"
              >
                Upload and Process
              </FormButton>
              <FormButton
                onClick={handleCancel}
                disabled={uploadMutation.isPending}
                variant="secondary"
              >
                Cancel
              </FormButton>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

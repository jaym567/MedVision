// frontend/src/hooks/useUploadDicom.ts

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { dicomApi } from '../services/dicomApi';
import { useToast } from './useToast';
import { ApiError } from '../types/api';

export const useUploadDicom = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (file: File) => dicomApi.uploadDicom(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['studies'] });
      showToast(
        data.message || 'DICOM file uploaded successfully',
        'success'
      );
      navigate(`/studies/${data.study.id}`);
    },
    onError: (error: ApiError) => {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Failed to upload DICOM file';
      showToast(message, 'error');
    },
  });
};

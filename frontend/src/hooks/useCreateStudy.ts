// frontend/src/hooks/useCreateStudy.ts
import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { createStudy } from '../services/studiesApi';
import type { StudyCreateRequest, StudyRead } from '../types/study';

export const useCreateStudy = (): UseMutationResult<
  StudyRead,
  Error,
  StudyCreateRequest
> => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: createStudy,
    onSuccess: (data) => {
      // Invalidate studies list to refetch with new study
      queryClient.invalidateQueries({ queryKey: ['studies'] });

      // Show success toast
      toast.success('Study created successfully');

      // Navigate to study detail page
      navigate(`/studies/${data.id}`);
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create study');
    },
  });
};

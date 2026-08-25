// frontend/src/hooks/useUpdateStudy.ts
import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { updateStudy } from '../services/studiesApi';
import type { StudyUpdate, StudyRead } from '../types/study';

interface UpdateStudyVariables {
  id: string;
  data: StudyUpdate;
}

export const useUpdateStudy = (): UseMutationResult<
  StudyRead,
  Error,
  UpdateStudyVariables
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: UpdateStudyVariables) => updateStudy(id, data),
    onSuccess: (data) => {
      // Invalidate and refetch the specific study
      queryClient.invalidateQueries({ queryKey: ['study', data.id] });

      // Invalidate studies list to show updated data
      queryClient.invalidateQueries({ queryKey: ['studies'] });

      toast.success('Study updated successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update study');
    },
  });
};

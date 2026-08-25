// frontend/src/hooks/useStudy.ts
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { getStudyById } from '../services/studiesApi';
import type { StudyRead } from '../types/study';

export const useStudy = (
  id: string | undefined
): UseQueryResult<StudyRead, Error> => {
  return useQuery({
    queryKey: ['study', id],
    queryFn: () => getStudyById(id!),
    enabled: !!id, // Only run query if id exists
    staleTime: 300000, // 5 minutes - study details change less frequently
  });
};

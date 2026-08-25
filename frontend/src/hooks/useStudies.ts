// frontend/src/hooks/useStudies.ts
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { getStudies } from '../services/studiesApi';
import type { StudyListResponse, StudyFilters } from '../types/study';

export const useStudies = (
  filters?: StudyFilters
): UseQueryResult<StudyListResponse, Error> => {
  return useQuery({
    queryKey: ['studies', filters],
    queryFn: () => getStudies(filters),
    staleTime: 60000, // 1 minute - studies list updates frequently
    placeholderData: (previousData) => previousData, // Keep previous data during refetch
  });
};

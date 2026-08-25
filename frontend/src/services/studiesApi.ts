// frontend/src/services/studiesApi.ts
import apiClient from './api';
import type {
  StudyCreateRequest,
  StudyRead,
  StudyListResponse,
  StudyFilters,
  StudyUpdate
} from '../types/study';

export const getStudies = async (filters?: StudyFilters): Promise<StudyListResponse> => {
  const params = new URLSearchParams();

  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.page_size) params.append('page_size', filters.page_size.toString());
  if (filters?.patient_id) params.append('patient_id', filters.patient_id);
  if (filters?.modality) params.append('modality', filters.modality);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.patient_name) params.append('patient_name', filters.patient_name);
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);

  const queryString = params.toString();
  const url = `/studies${queryString ? `?${queryString}` : ''}`;

  const response = await apiClient.get<StudyListResponse>(url);
  return response.data;
};

export const getStudyById = async (id: string): Promise<StudyRead> => {
  const response = await apiClient.get<StudyRead>(`/studies/${id}`);
  return response.data;
};

export const createStudy = async (data: StudyCreateRequest): Promise<StudyRead> => {
  const response = await apiClient.post<StudyRead>('/studies', data);
  return response.data;
};

export const updateStudy = async (id: string, data: StudyUpdate): Promise<StudyRead> => {
  const response = await apiClient.patch<StudyRead>(`/studies/${id}`, data);
  return response.data;
};

// frontend/src/types/study.ts
import type { UserSummary } from './user';

export enum StudyModality {
  DX = 'DX',
  CR = 'CR',
  CT = 'CT',
  MR = 'MR',
  US = 'US',
  XA = 'XA',
  NM = 'NM',
  PT = 'PT',
  OTHER = 'OTHER',
}

export enum StudyStatus {
  CREATED = 'created',
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  READY = 'ready',
  FAILED = 'failed',
  ARCHIVED = 'archived',
}

export interface PatientInfo {
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  sex: 'M' | 'F' | 'O';
  medical_history?: string;
}

export interface StudyCreate {
  modality: StudyModality;
  body_part_examined?: string;
  study_description?: string;
  study_date: string;
  accession_number?: string;
  metadata?: Record<string, any>;
}

export interface StudyCreateRequest {
  patient: PatientInfo;
  study: StudyCreate;
}

export interface StudyUpdate {
  status?: StudyStatus;
  body_part_examined?: string;
  study_description?: string;
  metadata?: Record<string, any>;
}

export interface StudySummary {
  id: string;
  modality: StudyModality;
  body_part_examined?: string;
  study_description?: string;
  study_date: string;
  status: StudyStatus;
  patient_id: string;
  patient_mrn: string;
  patient_first_name: string;
  patient_last_name: string;
  created_at: string;
}

export interface StudyRead extends StudySummary {
  accession_number?: string;
  metadata?: Record<string, any>;
  created_by_id: string;
  updated_at: string;
  patient: {
    id: string;
    mrn: string;
    first_name: string;
    last_name: string;
    date_of_birth: string;
    sex: 'M' | 'F' | 'O';
    medical_history?: string;
    display_name: string;
  };
  created_by: UserSummary;
}

export interface StudyListResponse {
  items: StudySummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface StudyFilters {
  page?: number;
  page_size?: number;
  patient_id?: string;
  modality?: StudyModality;
  status?: StudyStatus;
  patient_name?: string;
  date_from?: string;
  date_to?: string;
}

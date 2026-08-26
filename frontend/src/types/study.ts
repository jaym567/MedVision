// frontend/src/types/study.ts
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

export interface StudyRead {
  id: string;
  modality: StudyModality;
  body_part?: string; // Backend uses body_part, not body_part_examined
  study_description?: string;
  study_date: string;
  status: StudyStatus;
  accession_number?: string;
  metadata_json?: Record<string, any>; // Backend uses metadata_json
  study_instance_uid?: string;
  source?: string;
  storage_path?: string;
  created_at: string;
  updated_at: string;
  patient: {
    id: string;
    mrn: string;
    first_name: string;
    last_name: string;
    date_of_birth: string;
    sex: 'M' | 'F' | 'O';
    medical_history?: string;
    created_at: string;
    updated_at: string;
  };
  created_by_user: { // Backend uses created_by_user, not created_by
    id: string;
    email: string;
    full_name: string;
  };
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

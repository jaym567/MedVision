// frontend/src/types/study.ts
/**
 * Study types matching backend schemas
 */

import { PatientCreate, PatientSummary, PatientRead } from "./patient";
import { UserSummary } from "./user";
import { PaginatedResponse } from "./api";

export enum StudyModality {
  DX = "DX",
  CR = "CR",
  CT = "CT",
  MR = "MR",
  US = "US",
  XA = "XA",
  NM = "NM",
  PT = "PT",
  OTHER = "OTHER"
}

export enum StudyStatus {
  CREATED = "created",
  UPLOADED = "uploaded",
  PROCESSING = "processing",
  READY = "ready",
  FAILED = "failed",
  ARCHIVED = "archived"
}

export interface StudyCreate {
  accession_number: string;
  modality: StudyModality;
  body_part?: string;
  study_description: string;
  study_date: string; // ISO date string
  metadata_json?: Record<string, any>;
}

export interface StudyCreateRequest {
  patient: PatientCreate;
  study: StudyCreate;
}

export interface StudyUpdate {
  accession_number?: string;
  modality?: StudyModality;
  body_part?: string;
  study_description?: string;
  study_date?: string;
  status?: StudyStatus;
  metadata_json?: Record<string, any>;
}

export interface StudyRead {
  id: string;
  patient_id: string;
  created_by_user_id: string;
  study_instance_uid: string | null;
  accession_number: string;
  modality: StudyModality;
  body_part: string | null;
  study_description: string;
  study_date: string;
  status: StudyStatus;
  source: string;
  metadata_json: Record<string, any> | null;
  storage_path: string | null;
  created_at: string;
  updated_at: string;
  patient: PatientRead;
  created_by_user: UserSummary;
}

export interface StudySummary {
  id: string;
  accession_number: string;
  modality: StudyModality;
  body_part: string | null;
  study_description: string;
  study_date: string;
  status: StudyStatus;
  created_at: string;
  patient: PatientSummary;
}

export interface StudyListResponse extends PaginatedResponse<StudySummary> {
  // Inherits: items, total, page, page_size, total_pages
}

export interface StudyFilters {
  page?: number;
  page_size?: number;
  patient_id?: string;
  modality?: StudyModality;
  status?: StudyStatus;
  patient_name?: string;
  date_from?: string; // ISO date string
  date_to?: string; // ISO date string
}

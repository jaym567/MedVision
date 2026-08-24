// frontend/src/types/patient.ts
/**
 * Patient types matching backend schemas
 * WARNING: Use mock/de-identified data only
 */

export interface PatientCreate {
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string; // ISO date string
  sex: "M" | "F" | "O";
  medical_history?: string;
}

export interface PatientRead {
  id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  sex: "M" | "F" | "O";
  medical_history: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientSummary {
  id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  display_name: string;
}

// frontend/src/types/dicom.ts

export interface DicomMetadataSchema {
  // Patient Information
  patient_id?: string;
  patient_name?: string;
  patient_birth_date?: string;
  patient_sex?: string;

  // Study Information
  study_instance_uid?: string;
  study_date?: string;
  study_description?: string;
  accession_number?: string;

  // Series Information
  series_instance_uid?: string;
  modality?: string;
  body_part_examined?: string;

  // Instance Information
  sop_instance_uid?: string;

  // Equipment Information
  manufacturer?: string;
  manufacturer_model_name?: string;
  station_name?: string;

  // Image Information
  rows?: number;
  columns?: number;
  pixel_spacing?: string;
  slice_thickness?: string;
  window_center?: string;
  window_width?: string;
  photometric_interpretation?: string;
}

export interface DicomUploadResponse {
  study: {
    id: number;
    patient_id: number;
    study_instance_uid: string;
    accession_number?: string;
    study_date?: string;
    modality?: string;
    description?: string;
    status: string;
    source?: string;
    storage_path?: string;
    metadata_json?: Record<string, unknown>;
    created_at: string;
    updated_at: string;
  };
  dicom_metadata: DicomMetadataSchema;
  message: string;
}

// frontend/src/services/dicomApi.ts

import apiClient from './apiClient';
import { DicomUploadResponse } from '../types/dicom';

export const dicomApi = {
  uploadDicom: async (file: File): Promise<DicomUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<DicomUploadResponse>(
      '/studies/upload-dicom',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },
};

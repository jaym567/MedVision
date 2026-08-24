// frontend/src/utils/formatting.ts
/**
 * General formatting utilities
 */

import { UserRole } from "../types/user";
import { StudyModality, StudyStatus } from "../types/study";

/**
 * Format patient name from first and last name
 * @param firstName - Patient first name
 * @param lastName - Patient last name
 * @returns Formatted full name
 */
export function formatPatientName(
  firstName: string | null | undefined,
  lastName: string | null | undefined
): string {
  if (!firstName && !lastName) return "Unknown Patient";
  if (!firstName) return lastName || "Unknown";
  if (!lastName) return firstName;
  return `${firstName} ${lastName}`;
}

/**
 * Format MRN for display (uppercase)
 * @param mrn - Medical Record Number
 * @returns Uppercase MRN
 */
export function formatMRN(mrn: string | null | undefined): string {
  if (!mrn) return "N/A";
  return mrn.toUpperCase();
}

/**
 * Format user role for display
 * @param role - User role enum value
 * @returns Human-readable role
 */
export function formatRole(role: UserRole): string {
  const roleMap: Record<UserRole, string> = {
    [UserRole.PHYSICIAN]: "Physician",
    [UserRole.RESEARCHER]: "Researcher",
    [UserRole.ADMIN]: "Administrator",
  };
  return roleMap[role] || role;
}

/**
 * Get display label for modality
 * @param modality - Study modality
 * @returns Human-readable modality
 */
export function formatModality(modality: StudyModality): string {
  const modalityMap: Record<StudyModality, string> = {
    [StudyModality.DX]: "Digital Radiography",
    [StudyModality.CR]: "Computed Radiography",
    [StudyModality.CT]: "Computed Tomography",
    [StudyModality.MR]: "Magnetic Resonance",
    [StudyModality.US]: "Ultrasound",
    [StudyModality.XA]: "X-Ray Angiography",
    [StudyModality.NM]: "Nuclear Medicine",
    [StudyModality.PT]: "Positron Emission Tomography",
    [StudyModality.OTHER]: "Other",
  };
  return modalityMap[modality] || modality;
}

/**
 * Get display label for study status
 * @param status - Study status
 * @returns Human-readable status
 */
export function formatStatus(status: StudyStatus): string {
  const statusMap: Record<StudyStatus, string> = {
    [StudyStatus.CREATED]: "Created",
    [StudyStatus.UPLOADED]: "Uploaded",
    [StudyStatus.PROCESSING]: "Processing",
    [StudyStatus.READY]: "Ready",
    [StudyStatus.FAILED]: "Failed",
    [StudyStatus.ARCHIVED]: "Archived",
  };
  return statusMap[status] || status;
}

/**
 * Truncate long text with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text
 */
export function truncate(text: string | null | undefined, maxLength: number = 50): string {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
}

/**
 * Get user initials for avatar
 * @param fullName - User's full name
 * @returns Initials (e.g., "JS" for "Jane Smith")
 */
export function getUserInitials(fullName: string | null | undefined): string {
  if (!fullName) return "?";

  const parts = fullName.trim().split(" ");
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }

  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

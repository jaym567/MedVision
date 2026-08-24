// frontend/src/utils/date.ts
/**
 * Date formatting utilities for medical data display
 */

import { format, parseISO, differenceInYears } from "date-fns";

/**
 * Format ISO date string to readable format
 * @param isoDate - ISO date string from backend
 * @returns Formatted date string (e.g., "Jan 15, 2024")
 */
export function formatDate(isoDate: string | null | undefined): string {
  if (!isoDate) return "N/A";

  try {
    return format(parseISO(isoDate), "MMM dd, yyyy");
  } catch (error) {
    console.error("Invalid date:", isoDate);
    return "Invalid date";
  }
}

/**
 * Format ISO date string to date only (YYYY-MM-DD)
 * @param isoDate - ISO date string from backend
 * @returns Date only string
 */
export function formatDateOnly(isoDate: string | null | undefined): string {
  if (!isoDate) return "N/A";

  try {
    return format(parseISO(isoDate), "yyyy-MM-dd");
  } catch (error) {
    console.error("Invalid date:", isoDate);
    return "Invalid date";
  }
}

/**
 * Format ISO datetime string to readable datetime
 * @param isoDateTime - ISO datetime string from backend
 * @returns Formatted datetime string (e.g., "Jan 15, 2024 at 2:30 PM")
 */
export function formatDateTime(isoDateTime: string | null | undefined): string {
  if (!isoDateTime) return "N/A";

  try {
    return format(parseISO(isoDateTime), "MMM dd, yyyy 'at' h:mm a");
  } catch (error) {
    console.error("Invalid datetime:", isoDateTime);
    return "Invalid datetime";
  }
}

/**
 * Calculate age from date of birth
 * @param dateOfBirth - ISO date string
 * @returns Age in years
 */
export function calculateAge(dateOfBirth: string | null | undefined): number | null {
  if (!dateOfBirth) return null;

  try {
    return differenceInYears(new Date(), parseISO(dateOfBirth));
  } catch (error) {
    console.error("Invalid date of birth:", dateOfBirth);
    return null;
  }
}

/**
 * Get today's date in ISO format for form defaults
 * @returns Today's date as YYYY-MM-DD string
 */
export function getTodayISO(): string {
  return format(new Date(), "yyyy-MM-dd");
}

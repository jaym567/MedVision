// frontend/src/utils/validation.ts
/**
 * Form validation utilities
 */

/**
 * Validate email format
 * @param email - Email address to validate
 * @returns True if valid email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength (min 8 characters)
 * @param password - Password to validate
 * @returns Validation result
 */
export function validatePassword(password: string): { valid: boolean; message?: string } {
  if (password.length < 8) {
    return { valid: false, message: "Password must be at least 8 characters" };
  }
  return { valid: true };
}

/**
 * Validate MRN format (alphanumeric)
 * @param mrn - Medical Record Number
 * @returns True if valid MRN format
 */
export function isValidMRN(mrn: string): boolean {
  const mrnRegex = /^[A-Z0-9-]+$/i;
  return mrnRegex.test(mrn);
}

/**
 * Validate JSON string
 * @param jsonString - JSON string to validate
 * @returns Validation result
 */
export function validateJSON(jsonString: string): { valid: boolean; message?: string } {
  if (!jsonString.trim()) {
    return { valid: true }; // Empty is valid
  }

  try {
    JSON.parse(jsonString);
    return { valid: true };
  } catch (error) {
    return { valid: false, message: "Invalid JSON format" };
  }
}

/**
 * Validate date is not in the future
 * @param dateString - ISO date string
 * @returns True if date is today or in the past
 */
export function isDateNotFuture(dateString: string): boolean {
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(23, 59, 59, 999); // End of today
  return date <= today;
}

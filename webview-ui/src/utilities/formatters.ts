/**
 * Format a duration in milliseconds to a human-readable string (MM:SS)
 * @param ms Duration in milliseconds
 * @returns Formatted string like "2:05" or "15:30"
 */
export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

/**
 * Get current time formatted as a locale time string
 * @returns Formatted time string like "10:30:45 AM"
 */
export function getCurrentTimeString(): string {
  return new Date().toLocaleTimeString();
}

/**
 * Format a timestamp to a locale time string
 * @param timestamp Timestamp in milliseconds
 * @returns Formatted time string like "10:30:45 AM"
 */
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString();
}

/**
 * Parse step number from a log message
 * Matches patterns like "STEP_1", "STEP 2", "Step 3", "STEP_4_PASSED", etc.
 * @param message Log message to parse
 * @returns Step number if found, null otherwise
 */
export function parseStepNumber(message: string): number | null {
  const stepMatch = message.match(/STEP[_\s]*(\d+)(?:_[A-Z]+)?/i);
  if (stepMatch) {
    const stepNum = parseInt(stepMatch[1], 10);
    return isNaN(stepNum) ? null : stepNum;
  }
  return null;
}

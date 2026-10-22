export * from "./constants.js";

export function formatDate(isoString: string): string {
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
}

export function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, "");
}

// Base URL of the FastAPI backend. Override with VITE_API_URL in frontend/.env
export const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

// FastAPI reports errors as { detail: "..." } (or a list of validation errors).
export function getErrorMessage(data, fallback) {
  if (data && typeof data.detail === "string") {
    return data.detail;
  }

  if (data && Array.isArray(data.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg;
  }

  return fallback;
}

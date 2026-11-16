import { Capacitor } from "@capacitor/core";
import type { Account, Offer, RideRequest, Trip } from "../types";

const defaultApiUrl = Capacitor.getPlatform() === "android"
  ? "https://localhost:8000"
  : "https://localhost:8000";
const desktopApiUrl = new URLSearchParams(window.location.search).get("apiUrl");
const API_URL = import.meta.env.VITE_API_URL ?? desktopApiUrl ?? defaultApiUrl;
let sessionToken: string | null = null;

export function setSessionToken(token: string | null) {
  sessionToken = token;
}

export function getSessionToken() {
  return sessionToken;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (new URL(API_URL).protocol !== "https:") {
    throw new Error("Wasla requires an HTTPS API endpoint.");
  }
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (sessionToken) headers.set("Authorization", `Bearer ${sessionToken}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.error?.message ?? "The service could not complete your request.";
    throw new Error(message);
  }
  return data as T;
}

export async function signIn(email: string, password: string) {
  return api<{ account: Account; accessToken: string }>("/api/auth/login", {
    method: "POST", body: JSON.stringify({ email, password }),
  });
}

export async function signUp(input: {
  displayName: string; email: string; phone: string; password: string;
  preferredLanguage: "ar" | "en"; accountType: "individual" | "business";
}) {
  return api<{ account: Account; accessToken: string }>("/api/auth/register", {
    method: "POST", body: JSON.stringify(input),
  });
}

export const browseRequests = (type?: string, offset = 0, limit = 20) => {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (type) params.set("serviceType", type);
  return api<{ requests: RideRequest[]; total: number }>(`/api/requests?${params}`);
};
export const requestDetails = (id: string) =>
  api<{ request: RideRequest; offers: Offer[]; trip: Trip | null }>(`/api/requests/${id}`);
export const myTrips = () => api<{ trips: Trip[] }>("/api/trips");

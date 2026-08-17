/**
 * API client SiapQuiz — satu-satunya jalur HTTP ke backend.
 *
 * Mengurus: base URL dari env, penyisipan header Authorization, refresh token
 * otomatis pada 401 (diserialkan agar hanya satu refresh berjalan), dan
 * penerjemahan Problem Details (RFC 9457) menjadi error ber-code (coding-standard §4.1).
 */

export class ApiError extends Error {
  code: string;
  status: number;
  detail: string;

  constructor(code: string, status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.detail = detail;
  }
}

// Base URL API. Di browser, API_BASE_URL di-inline saat build (next public env).
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost/api/v1";

type RefreshHandler = () => Promise<string | null>;

// Mengizinkan store auth mendaftarkan callback refresh (dipasang sekali di auth-store).
let refreshHandler: RefreshHandler | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function setRefreshHandler(handler: RefreshHandler | null) {
  refreshHandler = handler;
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.__SIAPQUIZ_ACCESS__ ?? null;
}

export function setAccessToken(token: string | null) {
  if (typeof window !== "undefined") {
    window.__SIAPQUIZ_ACCESS__ = token;
  }
}

// Access token disimpan di memori (bukan localStorage) — sesi dijaga oleh
// refresh token httpOnly; token JWT tidak pernah dipersist.
declare global {
  interface Window {
    __SIAPQUIZ_ACCESS__?: string | null;
  }
}

async function refreshOnce(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  if (!refreshHandler) return null;
  refreshPromise = refreshHandler().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  /** Izinkan sekali retry otomatis setelah refresh (default true). */
  autoRefresh?: boolean;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const method = options.method ?? "GET";
  const headers: Record<string, string> = {
    ...(options.headers ?? {}),
  };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const doFetch = async (): Promise<Response> => {
    return fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      credentials: "include", // kirim cookie refresh httpOnly
    });
  };

  let response = await doFetch();

  if (response.status === 401 && options.autoRefresh !== false) {
    const newToken = await refreshOnce();
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      response = await doFetch();
    }
  }

  if (!response.ok) {
    throw await toApiError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = "REQUEST_FAILED";
  let detail = `Permintaan gagal (${response.status})`;
  try {
    const body = await response.json();
    code = body?.code ?? code;
    detail = body?.detail ?? detail;
  } catch {
    // body bukan JSON — pakai default
  }
  return new ApiError(code, response.status, detail);
}

export const api = {
  get: <T>(path: string, opts?: RequestOptions) =>
    apiFetch<T>(path, { ...opts, method: "GET" }),
  post: <T>(path: string, body?: unknown, opts?: RequestOptions) =>
    apiFetch<T>(path, { ...opts, method: "POST", body }),
  patch: <T>(path: string, body?: unknown, opts?: RequestOptions) =>
    apiFetch<T>(path, { ...opts, method: "PATCH", body }),
  del: <T>(path: string, opts?: RequestOptions) =>
    apiFetch<T>(path, { ...opts, method: "DELETE" }),
};

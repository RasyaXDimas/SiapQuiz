/**
 * Store auth SiapQuiz (zustand) — menyimpan user + peran sesi aktif.
 *
 * Sesi dijaga oleh refresh token httpOnly (cookie); access token disimpan di
 * memori (window.__SIAPQUIZ_ACCESS__) dan diisi ulang otomatis oleh api-client
 * saat 401. Store ini juga mendaftarkan callback refresh ke api-client.
 */

import { create } from "zustand";

import { api, setAccessToken, setRefreshHandler } from "@/lib/api-client";

export type Role = "TEACHER" | "STUDENT" | "ADMIN";

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  role: Role;
  organization_id: string;
  created_at: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

interface AuthState {
  user: AuthUser | null;
  initializing: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (data: {
    email: string;
    password: string;
    display_name: string;
    role: "TEACHER" | "STUDENT";
  }) => Promise<AuthUser>;
  logout: () => Promise<void>;
  loadSession: () => Promise<void>;
}

async function refreshAccessToken(): Promise<string | null> {
  try {
    const res = await api.post<AuthResponse>("/auth/refresh");
    setAccessToken(res.access_token);
    return res.access_token;
  } catch {
    setAccessToken(null);
    return null;
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  initializing: true,

  async login(email, password) {
    const res = await api.post<AuthResponse>("/auth/login", { email, password });
    setAccessToken(res.access_token);
    set({ user: res.user });
    return res.user;
  },

  async register(data) {
    const res = await api.post<AuthResponse>("/auth/register", data);
    setAccessToken(res.access_token);
    set({ user: res.user });
    return res.user;
  },

  async logout() {
    try {
      await api.post<void>("/auth/logout");
    } finally {
      setAccessToken(null);
      set({ user: null });
    }
  },

  async loadSession() {
    try {
      const user = await api.get<AuthUser>("/auth/me");
      set({ user, initializing: false });
    } catch {
      set({ user: null, initializing: false });
    }
  },
}));

// Daftarkan refresh handler ke api-client (sekali saat modul di-load).
setRefreshHandler(refreshAccessToken);

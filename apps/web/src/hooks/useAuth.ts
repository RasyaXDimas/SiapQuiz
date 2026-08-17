/**
 * Hook useAuth — akses store auth + guard peran untuk proteksi rute (S1-13).
 *
 * Contoh:
 *   const { user, loading } = useAuth("TEACHER");
 *   if (loading) return <Skeleton />;
 *   if (!user) redirect("/login");
 */

"use client";

import { useEffect } from "react";

import { useAuthStore } from "@/stores/authStore";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const initializing = useAuthStore((s) => s.initializing);
  const loadSession = useAuthStore((s) => s.loadSession);

  useEffect(() => {
    void loadSession();
  }, [loadSession]);

  return { user, loading: initializing, loadSession };
}

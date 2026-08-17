/**
 * Komponen guard rute berbasis peran (S1-13).
 *
 * Belum login → redirect /login. Peran tidak cocok → redirect ke area sesuai
 * peran (/t untuk guru, /s untuk siswa). Render null saat memuat sesi.
 */

"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/hooks/useAuth";
import type { Role } from "@/stores/authStore";

interface RequireRoleProps {
  roles: Role[];
  children: React.ReactNode;
}

export function RequireRole({ roles, children }: RequireRoleProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    if (!roles.includes(user.role)) {
      router.replace(user.role === "TEACHER" ? "/t" : "/s");
    }
  }, [user, loading, roles, router]);

  if (loading || !user || !roles.includes(user.role)) {
    return null;
  }

  return <>{children}</>;
}

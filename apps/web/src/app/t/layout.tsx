/**
 * Layout area guru (/t) — S1-13.
 * Navbar: Dokumen, Bank Soal, Kelas + menu pengguna. Dibatasi peran TEACHER.
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { RequireRole } from "@/components/features/RequireRole";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/stores/authStore";

export default function TeacherLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter();
  const { user } = useAuth();
  const logout = useAuthStore((s) => s.logout);

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <RequireRole roles={["TEACHER", "ADMIN"]}>
      <div className="min-h-screen bg-background text-foreground">
        <header className="border-b border-border bg-muted/50">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
            <span className="text-lg font-semibold tracking-wide">SiapQuiz</span>
            <nav className="flex items-center gap-6 text-sm font-medium">
              <Link href="/t" className="text-foreground hover:text-primary">
                Dokumen
              </Link>
              <Link href="/t" className="text-muted-foreground hover:text-primary">
                Bank Soal
              </Link>
              <Link href="/t" className="text-muted-foreground hover:text-primary">
                Kelas
              </Link>
            </nav>
            <div className="flex items-center gap-3 text-sm">
              <span className="text-muted-foreground">{user?.display_name}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Keluar
              </Button>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </div>
    </RequireRole>
  );
}

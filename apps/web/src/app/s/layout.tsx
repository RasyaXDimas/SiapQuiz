/**
 * Layout area siswa (/s) — S1-13.
 * Navbar sederhana + batasan peran STUDENT.
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { RequireRole } from "@/components/features/RequireRole";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/stores/authStore";

export default function StudentLayout({
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
    <RequireRole roles={["STUDENT"]}>
      <div className="min-h-screen bg-background text-foreground">
        <header className="border-b border-border bg-muted/50">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
            <span className="text-lg font-semibold tracking-wide">SiapQuiz</span>
            <nav className="flex items-center gap-4 text-sm font-medium">
              <Link href="/s" className="text-foreground hover:text-primary">
                Kuis Saya
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

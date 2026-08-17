/**
 * Halaman Register (/register) — wireframe 01-auth.md.
 * Tab Daftar: pilih peran (Pengajar/Siswa), nama tampilan, email, password
 * dengan indikator kekuatan. Berhasil → redirect sesuai peran.
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { useAuthStore } from "@/stores/authStore";

type RoleOption = "TEACHER" | "STUDENT";

function passwordStrength(pw: string): { label: string; color: string } {
  let score = 0;
  if (pw.length >= 8) score += 1;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score += 1;
  if (/\d/.test(pw)) score += 1;
  if (/[^A-Za-z0-9]/.test(pw)) score += 1;
  const labels = [
    { label: "Lemah", color: "bg-danger" },
    { label: "Cukup", color: "bg-warning" },
    { label: "Baik", color: "bg-info" },
    { label: "Kuat", color: "bg-success" },
  ];
  return labels[Math.min(score, 3)] ?? labels[0];
}

export default function RegisterPage() {
  const router = useRouter();
  const register = useAuthStore((s) => s.register);
  const [role, setRole] = useState<RoleOption>("TEACHER");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const strength = passwordStrength(password);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const user = await register({
        email,
        password,
        display_name: displayName,
        role,
      });
      router.replace(user.role === "TEACHER" ? "/t" : "/s");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail || "Gagal mendaftar. Coba lagi.");
      } else {
        setError("Terjadi kesalahan. Coba lagi.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold">SiapQuiz</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Soal dari materi Anda sendiri.
          </p>
        </div>

        <div className="rounded-md border border-border bg-background p-6 shadow-card">
          <div className="mb-6 grid grid-cols-2 rounded-md bg-muted p-1 text-sm font-medium">
            <Link
              href="/login"
              className="rounded-md px-4 py-2 text-center text-muted-foreground"
            >
              Masuk
            </Link>
            <Link
              href="/register"
              className="rounded-md bg-background px-4 py-2 text-center text-foreground shadow-sm"
            >
              Daftar
            </Link>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <fieldset>
              <legend className="mb-2 text-sm font-medium text-foreground">
                Saya adalah:
              </legend>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="role"
                    value="TEACHER"
                    checked={role === "TEACHER"}
                    onChange={() => setRole("TEACHER")}
                    className="h-4 w-4 accent-primary"
                  />
                  Pengajar
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="role"
                    value="STUDENT"
                    checked={role === "STUDENT"}
                    onChange={() => setRole("STUDENT")}
                    className="h-4 w-4 accent-primary"
                  />
                  Siswa
                </label>
              </div>
            </fieldset>

            <div>
              <label
                htmlFor="display_name"
                className="mb-1 block text-sm font-medium text-foreground"
              >
                Nama tampilan
              </label>
              <input
                id="display_name"
                type="text"
                required
                minLength={1}
                maxLength={80}
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Nama yang tampil di leaderboard"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="mb-1 block text-sm font-medium text-foreground"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="nama@contoh.com"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-1 block text-sm font-medium text-foreground"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                maxLength={128}
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Minimal 8 karakter"
              />
              {password.length > 0 && (
                <div className="mt-2">
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className={`h-full ${strength.color}`}
                      style={{ width: `${Math.min(password.length * 12, 100)}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Kekuatan: {strength.label}
                  </p>
                </div>
              )}
            </div>

            {error && (
              <p className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
                {error}
              </p>
            )}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Mendaftarkan..." : "Daftar"}
            </Button>
          </form>
        </div>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Punya kode kuis?{" "}
          <Link href="/join" className="text-primary">
            Gabung kuis
          </Link>
        </p>
      </div>
    </main>
  );
}

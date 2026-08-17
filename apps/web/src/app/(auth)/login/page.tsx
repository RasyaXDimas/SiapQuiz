/**
 * Halaman Login (/login) — wireframe 01-auth.md.
 * Tab Masuk: email + password. Berhasil → redirect sesuai peran.
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { useAuthStore } from "@/stores/authStore";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const user = await login(email, password);
      router.replace(user.role === "TEACHER" ? "/t" : "/s");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail || "Email atau password salah.");
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
              className="rounded-md bg-background px-4 py-2 text-center text-foreground shadow-sm"
            >
              Masuk
            </Link>
            <Link
              href="/register"
              className="rounded-md px-4 py-2 text-center text-muted-foreground"
            >
              Daftar
            </Link>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
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
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
                {error}
              </p>
            )}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Memasukkan..." : "Masuk"}
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-muted-foreground">
            Lupa password? (tidak aktif di v1)
          </p>
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

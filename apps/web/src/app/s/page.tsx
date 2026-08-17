/**
 * Halaman siswa (/s) — placeholder navigasi (S1-13).
 */

import { Gamepad2 } from "lucide-react";

export default function StudentHomePage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Halaman Siswa</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Riwayat kuis dan kode gabung tersedia mulai sprint berikutnya.
      </p>
      <div className="mt-8 max-w-md rounded-md border border-border bg-background p-6 shadow-card">
        <div className="mb-4 inline-flex rounded-md bg-primary/10 p-3">
          <Gamepad2 className="h-5 w-5 text-primary" />
        </div>
        <h3 className="text-lg font-semibold">Gabung Kuis</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Masukkan kode dari guru untuk mulai mengerjakan.
        </p>
      </div>
    </div>
  );
}

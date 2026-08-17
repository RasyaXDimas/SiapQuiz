/**
 * Dashboard guru (/t) — placeholder navigasi (S1-13).
 * Kartu statistik dibuat setelah datanya ada (sprint berikutnya).
 */

import { FileText, Sparkles, Users } from "lucide-react";

export default function TeacherDashboardPage() {
  const items = [
    {
      icon: FileText,
      title: "Dokumen",
      description: "Unggah materi dan kelola dokumen.",
    },
    {
      icon: Sparkles,
      title: "Bank Soal",
      description: "Generate dan tinjau soal tergrounded.",
    },
    {
      icon: Users,
      title: "Kelas",
      description: "Buat kelas dan sesi kuis real-time.",
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold">Dashboard Guru</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Menu lengkap tersedia mulai sprint berikutnya.
      </p>
      <div className="mt-8 grid gap-6 sm:grid-cols-3">
        {items.map(({ icon: Icon, title, description }) => (
          <div
            key={title}
            className="rounded-md border border-border bg-background p-6 shadow-card"
          >
            <div className="mb-4 inline-flex rounded-md bg-primary/10 p-3">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

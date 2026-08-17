import { FileText, Quote, Sparkles, Trophy, Users } from "lucide-react";

import { Button } from "@/components/ui/button";

// Landing halaman Sprint 0 — memakai token warna design-system
// (bg-background, text-primary, bg-muted, border, dsb.) supaya terlihat
// Tailwind aktif sejak menit pertama.
export default function LandingPage() {
  const features = [
    {
      icon: FileText,
      title: "Materi jadi kuis",
      description: "PDF, DOCX, PPTX dari dosen diubah jadi soal pilihan ganda.",
      color: "text-info",
      bg: "bg-info/10",
    },
    {
      icon: Quote,
      title: "Kutipan terverifikasi",
      description:
        "Setiap soal membawa kutipan sumber dari dokumen asli. Tanpa kutipan, soal dibuang otomatis.",
      color: "text-success",
      bg: "bg-success/10",
    },
    {
      icon: Users,
      title: "Real-time & leaderboard",
      description:
        "Siswa mengerjakan langsung, peringkat diperbarui saat itu juga.",
      color: "text-primary",
      bg: "bg-primary/10",
    },
  ];

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-muted/50">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold tracking-wide">SiapQuiz</span>
          <nav className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Masuk</span>
            <Button size="sm">Daftar</Button>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-20 text-center">
        <h1 className="text-3xl font-bold sm:text-4xl">
          Materi dosen Anda, jadi kuis yang{" "}
          <span className="text-primary">terbukti sumbernya</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
          SiapQuiz mengubah dokumen perkuliahan menjadi kuis pilihan ganda yang
          dikerjakan siswa secara online real-time. Setiap soal membawa kutipan
          sumber terverifikasi — soal yang kutipannya tidak ditemukan dibuang
          otomatis.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Button size="lg">
            <Sparkles className="h-4 w-4" />
            Mulai Membuat
          </Button>
          <Button variant="outline" size="lg">
            Lihat Cara Kerja
          </Button>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-6 px-6 pb-20 sm:grid-cols-3">
        {features.map(({ icon: Icon, title, description, color, bg }) => (
          <div
            key={title}
            className="rounded-md border border-border bg-background p-6 shadow-card"
          >
            <div className={`mb-4 inline-flex rounded-md p-3 ${bg}`}>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {description}
            </p>
          </div>
        ))}
      </section>

      <footer className="border-t border-border bg-muted/50">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-2">
            <Trophy className="h-4 w-4 text-warning" />
            SiapQuiz — kuis terverifikasi, pembelajaran bermakna
          </span>
          <span>Sprint 0 · Skeleton</span>
        </div>
      </footer>
    </main>
  );
}

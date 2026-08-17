import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import "./globals.css";

// Tipografi design-system.md: Inter (utama, variable self-hosted via next/font)
// dan JetBrains Mono (kutipan sumber).
const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SiapQuiz",
  description:
    "Ubah materi ajar menjadi kuis pilihan ganda yang terverifikasi sumber kutipannya, dikerjakan siswa secara real-time dengan leaderboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}

import type { Config } from "tailwindcss";

// Token warna dipetakan 1:1 dari project-docs/02-ux/design-system.md.
// Nilai hex didefinisikan sebagai CSS variable di globals.css (:root = light,
// @media prefers-color-scheme: dark = dark). Lihat design-system.md "Warna".
const config: Config = {
  darkMode: "media",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        muted: "var(--muted)",
        "muted-foreground": "var(--muted-foreground)",
        border: "var(--border)",
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
        info: "var(--info)",
        // Warna opsi jawaban A–E (design-system.md) — palet tetap agar siswa
        // mengenali posisi lewat warna, bukan hanya huruf.
        option: {
          a: "var(--option-a)",
          b: "var(--option-b)",
          c: "var(--option-c)",
          d: "var(--option-d)",
          e: "var(--option-e)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.1)",
      },
    },
  },
  plugins: [],
};

export default config;

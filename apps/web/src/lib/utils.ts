import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Pola shadcn/ui: clsx untuk kondisi + tailwind-merge agar class Tailwind
// tidak bentrok (coding-standard.md §4).
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

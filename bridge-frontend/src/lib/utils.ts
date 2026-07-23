import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
}

export function formatDateTime(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function formatRelativeWindow(iso: string) {
  const diffMs = new Date(iso).getTime() - Date.now();
  const hours = Math.round(diffMs / (1000 * 60 * 60));
  if (hours <= 0) return "window closed";
  if (hours === 1) return "1 hour left";
  return `${hours} hours left`;
}

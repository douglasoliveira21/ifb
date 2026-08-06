import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Instituto Fiscaliza Brasil - IFB",
  description:
    "Plataforma pública e apartidária que transforma dados públicos em informações claras sobre políticos brasileiros.",
  keywords: [
    "fiscalização",
    "transparência",
    "políticos",
    "dados públicos",
    "brasil",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="bg-white text-ifb-black font-sans antialiased">
        {children}
      </body>
    </html>
  );
}

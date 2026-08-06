"use client";

import { useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SUBJECTS = [
  "Dúvida",
  "Correção de dados",
  "Contestação",
  "Imprensa",
  "Parceria",
  "Doação",
  "Outro",
];

export default function ContatoPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name || !form.email || !form.subject || !form.message) return;

    setStatus("sending");
    try {
      const res = await fetch(`${API_URL}/api/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setStatus("sent");
        setForm({ name: "", email: "", subject: "", message: "" });
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-8">
          <Link href="/" className="text-[13px] text-[#9CA3AF] hover:text-[#111] transition mb-4 inline-block">← Início</Link>
          <h1 className="text-[28px] font-bold text-[#111]">Contato</h1>
          <p className="text-[14px] text-[#6B7280] mt-2">Entre em contato com a equipe do Instituto Fiscaliza Brasil.</p>
        </div>
      </div>

      <div className="max-w-[560px] mx-auto px-6 lg:px-12 py-10">
        {status === "sent" ? (
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-8 text-center">
            <div className="w-[56px] h-[56px] bg-[#DCFCE7] rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-7 h-7 text-[#16A34A]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <h2 className="text-[18px] font-bold text-[#111] mb-2">Mensagem enviada</h2>
            <p className="text-[13px] text-[#6B7280]">Retornaremos assim que possível. Obrigado pelo contato.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white border border-[#E5E7EB] rounded-[16px] p-6 space-y-5">
            <div>
              <label className="text-[12px] font-medium text-[#374151] block mb-1.5">Nome</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="w-full h-[44px] px-4 border border-[#E5E7EB] rounded-[10px] text-[14px] outline-none focus:ring-2 focus:ring-[#F4B400] focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="text-[12px] font-medium text-[#374151] block mb-1.5">E-mail</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                className="w-full h-[44px] px-4 border border-[#E5E7EB] rounded-[10px] text-[14px] outline-none focus:ring-2 focus:ring-[#F4B400] focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="text-[12px] font-medium text-[#374151] block mb-1.5">Assunto</label>
              <select
                value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                required
                className="w-full h-[44px] px-4 border border-[#E5E7EB] rounded-[10px] text-[14px] bg-white outline-none focus:ring-2 focus:ring-[#F4B400] focus:border-transparent transition"
              >
                <option value="">Selecione...</option>
                {SUBJECTS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[12px] font-medium text-[#374151] block mb-1.5">Mensagem</label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                required
                rows={5}
                className="w-full px-4 py-3 border border-[#E5E7EB] rounded-[10px] text-[14px] outline-none focus:ring-2 focus:ring-[#F4B400] focus:border-transparent transition resize-none"
              />
            </div>

            {status === "error" && (
              <p className="text-[13px] text-red-600">Erro ao enviar. Tente novamente.</p>
            )}

            <button
              type="submit"
              disabled={status === "sending"}
              className="w-full h-[44px] bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[14px] font-semibold rounded-[10px] transition-colors disabled:opacity-50"
            >
              {status === "sending" ? "Enviando..." : "Enviar mensagem"}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}

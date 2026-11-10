"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export default function SiteFooter() {
  const [footer, setFooter] = useState("ایران فردا؛ رسانه معلمان ایران");
  useEffect(() => { apiFetch<{ footer_text: string }>("/api/site-settings/").then(data => setFooter(data.footer_text)).catch(() => undefined); }, []);
  return <footer className="site-footer"><div className="footer-inner"><span>{footer}</span><span>جامعه‌ای برای گفتگو، یادگیری و هم‌اندیشی</span></div></footer>;
}

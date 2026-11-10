// چیدمان ریشه تمام صفحات؛ جهت راست‌به‌چپ و احراز هویت سراسری در این فایل تنظیم می‌شود.
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AuthProvider } from "@/components/AuthProvider";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import BottomNav from "@/components/BottomNav";
import CustomFontStyle from "@/components/CustomFontStyle";
import "./globals.css";

export const metadata: Metadata = {
  title: "ایران فردا | رسانه معلمان ایران",
  description: "شبکه اجتماعی و رسانه جامعه معلمان ایران",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="fa" dir="rtl">
      <body>
        <AuthProvider>
          <CustomFontStyle />
          <SiteHeader />
          <main>{children}</main>
          <BottomNav />
          <SiteFooter />
        </AuthProvider>
      </body>
    </html>
  );
}

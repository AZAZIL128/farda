"use client";

// صفحه ثبت‌نام کاربران جدید با نمایش لوگوی برند و اعتبارسنجی اولیه فرم
import { FormEvent, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: "", display_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // تغییر کنترل‌شده مقادیر فرم ثبت‌نام
  const update = (key: keyof typeof form, value: string) => setForm((old) => ({ ...old, [key]: value }));

  // ثبت حساب جدید و ورود خودکار پس از ایجاد موفق حساب
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { await register(form); router.push("/"); }
    catch (err) { setError(err instanceof Error ? err.message : "ثبت‌نام انجام نشد؛ اطلاعات را بررسی کنید."); }
    finally { setBusy(false); }
  };

  return <div className="auth-page"><div className="auth-card auth-card-large">
    <Link href="/" className="auth-logo"><Image src="/logo-iran-farda.png" alt="ایران فردا" width={300} height={95} priority /></Link>
    <span className="eyebrow">عضویت در جامعه</span><h1>ساخت حساب کاربری</h1><p className="auth-intro">به جمع معلمان و فعالان آموزشی ایران فردا بپیوندید.</p>
    <form onSubmit={submit} className="form-stack">
      <label>نام و نام خانوادگی<input value={form.display_name} onChange={(e) => update("display_name", e.target.value)} autoComplete="name" required /></label>
      <label>نام کاربری<input value={form.username} onChange={(e) => update("username", e.target.value)} autoComplete="username" minLength={3} maxLength={30} pattern="[A-Za-z0-9_]+" required /><small>فقط حروف انگلیسی، عدد و زیرخط مجاز است.</small></label>
      <label>ایمیل<input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} autoComplete="email" required /></label>
      <label>رمز عبور<input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} autoComplete="new-password" minLength={8} required /><small>حداقل ۸ نویسه؛ رمز نباید فقط عدد باشد.</small></label>
      {error && <div className="form-error">{error}</div>}
      <button className="button button-primary button-wide" disabled={busy}>{busy ? "در حال ساخت حساب..." : "ایجاد حساب کاربری"}</button>
    </form>
    <div className="auth-bottom">قبلاً عضو شده‌اید؟ <Link href="/login">وارد شوید</Link></div>
    <Link href="/" className="back-home">بازگشت به صفحه اصلی</Link>
  </div></div>;
}

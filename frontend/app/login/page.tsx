"use client";

// صفحه ورود کاربران؛ طراحی از لوگوی رسمی و رنگ‌های برند استفاده می‌کند.
import { FormEvent, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // ارسال اطلاعات ورود و هدایت کاربر به صفحه اصلی پس از موفقیت
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { await login(username, password); router.push("/"); }
    catch (err) { setError(err instanceof Error ? err.message : "نام کاربری یا رمز عبور صحیح نیست."); }
    finally { setBusy(false); }
  };

  return <div className="auth-page"><div className="auth-card">
    <Link href="/" className="auth-logo"><Image src="/logo-iran-farda.png" alt="ایران فردا" width={300} height={95} priority /></Link>
    <span className="eyebrow">خوش آمدید</span><h1>ورود به حساب کاربری</h1><p className="auth-intro">برای ادامه گفتگوها و دسترسی به امکانات جامعه وارد شوید.</p>
    <form onSubmit={submit} className="form-stack">
      <label>نام کاربری<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required /></label>
      <label>رمز عبور<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required /></label>
      {error && <div className="form-error">{error}</div>}
      <button className="button button-primary button-wide" disabled={busy}>{busy ? "در حال ورود..." : "ورود"}</button>
    </form>
    <div className="auth-bottom"><Link href="/forgot-password">فراموشی رمز عبور</Link></div>
    <div className="auth-bottom">حساب ندارید؟ <Link href="/register">ثبت‌نام کنید</Link></div>
    <Link href="/" className="back-home">بازگشت به صفحه اصلی</Link>
  </div></div>;
}

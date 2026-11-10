"use client";

// مدیریت وضعیت ورود در کل رابط کاربری؛ توکن‌ها فعلاً در localStorage نگهداری می‌شوند.
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { apiFetch } from "@/lib/api";
import type { User } from "@/lib/types";

type AuthContextValue = {
  user: User | null;
  ready: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: { username: string; email: string; display_name: string; password: string }) => Promise<void>;
  logout: () => void;
  reloadUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  // دریافت اطلاعات کاربر پس از بارگذاری برنامه یا تمدید صفحه
  const reloadUser = async () => {
    try {
      const current = await apiFetch<User>("/api/auth/me/");
      setUser(current);
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    const init = async () => {
      if (window.localStorage.getItem("if_access")) await reloadUser();
      setReady(true);
    };
    void init();
  }, []);

  // ورود با JWT و ذخیره access/refresh token
  const login = async (username: string, password: string) => {
    const tokens = await apiFetch<{ access: string; refresh: string }>("/api/auth/token/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    window.localStorage.setItem("if_access", tokens.access);
    window.localStorage.setItem("if_refresh", tokens.refresh);
    await reloadUser();
  };

  // ایجاد حساب و سپس ورود خودکار کاربر تازه ثبت‌نام‌شده
  const register = async (data: { username: string; email: string; display_name: string; password: string }) => {
    await apiFetch("/api/auth/register/", { method: "POST", body: JSON.stringify(data) });
    await login(data.username, data.password);
  };

  // خروج از حساب و پاک‌کردن توکن‌های مرورگر
  const logout = () => {
    window.localStorage.removeItem("if_access");
    window.localStorage.removeItem("if_refresh");
    setUser(null);
  };

  const value = useMemo(() => ({ user, ready, login, register, logout, reloadUser }), [user, ready]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// hook ساده برای دسترسی به وضعیت احراز هویت در صفحات و کامپوننت‌ها
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth باید داخل AuthProvider استفاده شود.");
  return context;
}

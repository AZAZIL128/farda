// ابزار مشترک ارتباط با API جنگو؛ همه درخواست‌ها از مسیر یکسان /api عبور می‌کنند.
export type ApiError = { detail?: string; [key: string]: unknown };

// خواندن توکن دسترسی ذخیره‌شده در مرورگر
function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("if_access");
}

// تمدید توکن منقضی‌شده با refresh token و ذخیره توکن جدید
async function refreshAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const refresh = window.localStorage.getItem("if_refresh");
  if (!refresh) return null;
  try {
    const response = await fetch("/api/auth/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!response.ok) throw new Error("refresh failed");
    const data = await response.json();
    window.localStorage.setItem("if_access", data.access);
    if (data.refresh) window.localStorage.setItem("if_refresh", data.refresh);
    return data.access as string;
  } catch {
    window.localStorage.removeItem("if_access");
    window.localStorage.removeItem("if_refresh");
    return null;
  }
}

// تابع عمومی درخواست که JSON، فرم و آپلود فایل را پشتیبانی می‌کند.
export async function apiFetch<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path.startsWith("/") ? path : `/api/${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  // اگر access token منقضی شده باشد، فقط یک بار آن را تمدید می‌کنیم.
  if (response.status === 401 && retry && token) {
    const newToken = await refreshAccessToken();
    if (newToken) return apiFetch<T>(path, options, false);
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({} as ApiError));
    const details = (data as ApiError).detail;
    const flatten = (value: unknown): string[] => {
      if (typeof value === "string") return [value];
      if (Array.isArray(value)) return value.flatMap(flatten);
      if (value && typeof value === "object") return Object.entries(value as Record<string, unknown>).flatMap(([key, item]) => {
        const labels: Record<string, string> = { username: "نام کاربری", email: "ایمیل", password: "رمز عبور", display_name: "نام نمایشی" };
        return (labels[key] ? [`${labels[key]}: `] : []).concat(flatten(item));
      });
      return [];
    };
    const messages = flatten(details ?? data);
    const message = messages.length ? messages.join("\n") : "در انجام درخواست خطایی رخ داد. اطلاعات واردشده را بررسی کنید.";
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

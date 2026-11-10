import type { NextConfig } from "next";

// خروجی standalone باعث می‌شود ایمیج Docker فرانت‌اند سبک‌تر شود.
const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
};

export default nextConfig;

"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function NotificationsPage(){const router=useRouter();useEffect(()=>{router.replace("/settings");},[router]);return <main className="page-shell"><div className="empty-state">در حال انتقال به بخش اعلان‌های حساب کاربری...</div></main>}

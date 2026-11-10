"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "./AuthProvider";

type HeaderSettings = {site_title:string;header_logo:string;header_logo_width:number;header_logo_position:string;header_background:string};
export default function SiteHeader() {
  const { user, logout, ready } = useAuth();
  const [settings,setSettings] = useState<HeaderSettings|null>(null);
  const [open,setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(()=>{apiFetch<HeaderSettings>("/api/site-settings/").then(v=>{setSettings(v);document.title=v.site_title;}).catch(()=>undefined);},[]);
  useEffect(()=>{const close=(e:MouseEvent)=>{if(ref.current&&!ref.current.contains(e.target as Node))setOpen(false);};const esc=(e:KeyboardEvent)=>{if(e.key==="Escape")setOpen(false);};document.addEventListener("mousedown",close);document.addEventListener("keydown",esc);return()=>{document.removeEventListener("mousedown",close);document.removeEventListener("keydown",esc);};},[]);
  const width=Math.min(500,Math.max(60,settings?.header_logo_width||220));
  return <header className="site-header" style={{background:settings?.header_background||undefined}}><div className={`header-inner header-logo-${settings?.header_logo_position||"right"}`}>
    <Link href="/" className="brand-link" aria-label="صفحه اصلی ایران فردا">{settings?.header_logo?<img src={settings.header_logo} alt={settings.site_title} style={{width,height:"auto",maxHeight:76,objectFit:"contain"}}/>:<img src="/logo-iran-farda.png" alt="ایران فردا" style={{width:250,height:"auto"}}/>}</Link>
    
    <div className="header-actions" ref={ref}>{!ready?<span className="muted">...</span>:user?<><button className="account-menu-trigger" onClick={()=>setOpen(v=>!v)} aria-expanded={open}>{user.avatar?<img src={user.avatar} alt="" onError={e=>{const parent=e.currentTarget.parentElement;if(parent){const fallback=document.createElement("span");fallback.textContent=(user.display_name||user.username).slice(0,1);e.currentTarget.remove();parent.prepend(fallback);}}}/>:<span>{(user.display_name||user.username).slice(0,1)}</span>}<b>{user.display_name||user.username}</b><span>⌄</span></button>{open&&<div className="account-menu"><strong>@{user.username}</strong><Link href={`/profile/${user.username}`} onClick={()=>setOpen(false)}>پروفایل من</Link><Link href="/settings" onClick={()=>setOpen(false)}>مدیریت حساب کاربری</Link>{(user.is_staff||user.is_superuser)&&<Link href="/admin-panel" onClick={()=>setOpen(false)}>پنل مدیریت و صفحه‌ساز</Link>}<button onClick={()=>{setOpen(false);logout();window.location.href="/";}}>خروج از حساب</button></div>}</>:<><Link className="button button-outline button-small" href="/login">ورود</Link><Link className="button button-primary button-small" href="/register">عضویت</Link></>}</div>
  </div></header>;
}

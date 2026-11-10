"use client";

import {useEffect,useState} from "react";
import {apiFetch} from "@/lib/api";

// قلم اختصاصی از تنظیمات عمومی دریافت می‌شود و روی تمام اجزای رابط کاربری اعمال می‌گردد.
export default function CustomFontStyle(){
 const [font,setFont]=useState<{url:string;name:string}|null>(null);
 useEffect(()=>{
  let active=true;
  const load=()=>apiFetch<any>("/api/site-settings/").then(x=>{
   if(!active)return;
   if(x.custom_font){setFont({url:x.custom_font,name:x.custom_font_name||"IranFardaCustom"});}
   else setFont(null);
  }).catch(()=>{});
  void load();
  // هنگام بازگشت کاربر به سایت، تنظیمات قلم دوباره بررسی می‌شود.
  const onFocus=()=>{void load();};
  window.addEventListener("focus",onFocus);
  window.addEventListener("if-site-settings-updated",onFocus);
  return ()=>{active=false;window.removeEventListener("focus",onFocus);window.removeEventListener("if-site-settings-updated",onFocus);};
 },[]);
 if(!font)return null;
 const family=font.name.replace(/[^a-zA-Z0-9_-]/g,"")||"IranFardaCustom";
 const url=font.url.replace(/\\/g,"\\\\").replace(/'/g,"%27");
 return <style jsx global>{`
  @font-face{font-family:'${family}';src:url('${url}');font-style:normal;font-weight:100 900;font-display:swap}
  html,body,body *{font-family:'${family}',Vazirmatn,Tahoma,sans-serif!important}
 `}</style>;
}

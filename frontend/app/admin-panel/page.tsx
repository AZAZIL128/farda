"use client";

// پنل مدیریتی اختصاصی؛ امکانات اصلی مدیریت از API محافظت‌شده جنگو دریافت می‌شوند.
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";

type Dashboard = { users: number; active_users: number; posts: number; visible_posts: number; open_reports: number; suspended_users: number };
type AdminUser = { id: number; username: string; email: string; display_name: string; is_verified: boolean; is_suspended: boolean; is_staff: boolean };
type AdminPost = { id: number; author__username: string; content: string; is_hidden: boolean; created_at: string };
type AdminReport = { id: number; reporter__username: string | null; post_id: number; reason: string; is_resolved: boolean };
type AdminFollow = { id: number; follower__username: string; following__username: string };
type SiteSettings = { header_custom:Record<string,any>; footer_custom:Record<string,any>; home_custom:Record<string,any>; custom_font:string; custom_font_name:string; header_logo: string; header_logo_width: number; header_logo_position: string; header_background: string; bottom_nav_background:string; bottom_nav_color:string; bottom_nav_active_color:string; bottom_nav_home_label:string; bottom_nav_explore_label:string; bottom_nav_following_label:string; site_title: string; hero_title: string; hero_highlight: string; hero_description: string; feed_title: string; about_title: string; about_text: string; features_title: string; features_text: string; footer_text: string; show_hero: boolean; show_about: boolean; show_features: boolean; show_join: boolean; post_max_words:number };

export default function AdminPanelPage() {
  const { user, ready } = useAuth();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [posts, setPosts] = useState<AdminPost[]>([]);
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [follows, setFollows] = useState<AdminFollow[]>([]);
  const [siteSettings, setSiteSettings] = useState<SiteSettings | null>(null);
  const [settingsMessage, setSettingsMessage] = useState("");
  const [headerLogoFile, setHeaderLogoFile] = useState<File | null>(null);
  const [fontFile, setFontFile] = useState<File | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
  const [userSearch, setUserSearch] = useState("");
  const [sendToAll, setSendToAll] = useState(false);
  const [notificationText, setNotificationText] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [pendingConfirm, setPendingConfirm] = useState<{kind:"post"|"follow";id:number}|null>(null);

  // بارگذاری هم‌زمان آمار، کاربران، پست‌ها و گزارش‌ها از API مدیریتی
  const load = useCallback(async () => {
    if (!user?.is_staff && !user?.is_superuser) { setLoading(false); return; }
    setLoading(true);
    try {
      const [stats, userRows, postRows, reportRows, followRows, siteConfig] = await Promise.all([
        apiFetch<Dashboard>("/api/admin/dashboard/"),
        apiFetch<AdminUser[]>(`/api/admin/users/${userSearch.trim() ? `?q=${encodeURIComponent(userSearch.trim())}` : ""}`),
        apiFetch<AdminPost[]>("/api/admin/posts/"),
        apiFetch<AdminReport[]>("/api/admin/reports/"),
        apiFetch<AdminFollow[]>("/api/admin/follows/"),
        apiFetch<SiteSettings>("/api/admin/site-settings/"),
      ]);
      setDashboard(stats); setUsers(userRows); setPosts(postRows); setReports(reportRows); setFollows(followRows); setSiteSettings(siteConfig);
    } catch (err) { setError(err instanceof Error ? err.message : "بارگذاری پنل مدیریت انجام نشد."); }
    finally { setLoading(false); }
  }, [user, userSearch]);

  useEffect(() => { if (ready) void load(); }, [ready, load]);

  // اجرای عملیات مدیریتی روی حساب کاربر
  const userAction = async (id: number, action: "suspend" | "verify") => {
    try { await apiFetch(`/api/admin/users/${id}/${action}/`, { method: "POST" }); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "عملیات کاربر انجام نشد."); }
  };

  // مخفی‌سازی/نمایش مجدد یا حذف پست
  const postAction = async (id: number, action: "hide" | "delete") => {
    
    try { await apiFetch(`/api/admin/posts/${id}/${action}/`, { method: "POST" }); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "عملیات پست انجام نشد."); }
  };

  // بستن گزارش پس از بررسی مدیر
  const resolveReport = async (id: number) => {
    try { await apiFetch(`/api/admin/reports/${id}/resolve/`, { method: "POST" }); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "رسیدگی به گزارش انجام نشد."); }
  };

  // ارسال اعلان مدیریتی برای کاربران انتخاب‌شده یا همه کاربران فعال
  const sendNotification = async () => {
    try {
      const result = await apiFetch<{ sent: number }>("/api/admin/notifications/send/", {
        method: "POST",
        body: JSON.stringify({ text: notificationText, recipient_ids: selectedUsers, send_to_all: sendToAll }),
      });
      setError(`اعلان با موفقیت برای ${result.sent} کاربر ارسال شد.`);
      setNotificationText(""); setSelectedUsers([]); setSendToAll(false);
    } catch (err) { setError(err instanceof Error ? err.message : "ارسال اعلان ناموفق بود."); }
  };

  // حذف رابطه دنبال‌کردن اشتباه یا نامعتبر با درخواست مدیر
  const removeFollow = async (id: number) => {
    
    try { await apiFetch(`/api/admin/follows/${id}/`, { method: "DELETE" }); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "حذف رابطه انجام نشد."); }
  };

  if (!ready || loading) return <div className="page-shell"><div className="empty-state">در حال بررسی دسترسی و بارگذاری پنل...</div></div>;
  if (!user || (!user.is_staff && !user.is_superuser)) return <div className="page-shell"><div className="empty-state"><strong>دسترسی مجاز نیست.</strong><span>این بخش فقط برای مدیر سامانه فعال است.</span><Link href="/" className="button button-primary">بازگشت به خانه</Link></div></div>;

  return <div className="page-shell admin-layout">
    <div className="admin-heading"><div><span className="eyebrow">مرکز کنترل سامانه</span><h1>پنل مدیریت ایران فردا</h1><p className="muted">مدیریت کاربران، محتوا و گزارش‌های ثبت‌شده</p></div><button className="refresh-fab admin-refresh admin-refresh-inline" type="button" aria-label="به‌روزرسانی اطلاعات" title="به‌روزرسانی اطلاعات" onClick={()=>void load()}><svg viewBox="0 0 24 24"><path d="M20 7v5h-5M4 17v-5h5M5.6 9a7 7 0 0 1 11.8-2L20 12M4 12l2.6 5a7 7 0 0 0 11.8-2"/></svg></button></div>
    {error && <div className="notice-bar">{error}</div>}
    {dashboard && <div className="stats-grid">
      <div className="stat-card"><span>کل کاربران</span><strong>{dashboard.users}</strong></div>
      <div className="stat-card"><span>کاربران فعال</span><strong>{dashboard.active_users}</strong></div>
      <div className="stat-card"><span>کل پست‌ها</span><strong>{dashboard.posts}</strong></div>
      <div className="stat-card"><span>گزارش‌های باز</span><strong>{dashboard.open_reports}</strong></div>
    </div>}

    {siteSettings && <details className="admin-section admin-collapsible"><summary><span><strong>تنظیم ظاهر و نوشته‌های سایت</strong><small>لوگو، قلم، رنگ‌ها و متن‌های سایت</small></span><b>ویرایش تنظیمات</b></summary><div className="admin-collapsible-body">
      <p className="muted small-text">تیتر صفحه اصلی، توضیحات و عنوان بخش‌های کناری را از اینجا تغییر بده. این تغییرات برای همه بازدیدکنندگان اعمال می‌شود.</p>
      <div className="header-builder-box">
        <h3>سازنده سربرگ سایت</h3>
        {siteSettings.header_logo && <img src={siteSettings.header_logo} alt="لوگوی فعلی" style={{maxWidth: "220px", maxHeight: "75px", objectFit: "contain"}} />}
        <div className="logo-upload-control"><span className="logo-upload-title">بارگذاری نشان تازه</span><input className="visually-hidden-file" id="admin-logo-file" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" onChange={e => setHeaderLogoFile(e.target.files?.[0] || null)} /><label htmlFor="admin-logo-file" className="button button-outline button-small">انتخاب تصویر لوگو</label><small>{headerLogoFile ? headerLogoFile.name : "PNG، JPG، WEBP یا SVG"}</small></div>
        <label>اندازه لوگو: {siteSettings.header_logo_width}px<input type="range" min="60" max="500" value={siteSettings.header_logo_width} onChange={e => setSiteSettings(old => old ? {...old, header_logo_width: Number(e.target.value)} : old)} /></label>
        <label>جایگاه لوگو<select value={siteSettings.header_logo_position} onChange={e => setSiteSettings(old => old ? {...old, header_logo_position:e.target.value} : old)}><option value="right">راست</option><option value="center">وسط</option><option value="left">چپ</option></select></label>
        <label>رنگ پس‌زمینه سربرگ<input type="color" value={siteSettings.header_background} onChange={e => setSiteSettings(old => old ? {...old, header_background:e.target.value} : old)} /></label>
        <div className="header-builder-preview" style={{background:siteSettings.header_background,justifyContent:siteSettings.header_logo_position === "left" ? "flex-start" : siteSettings.header_logo_position === "center" ? "center" : "flex-end"}}>{headerLogoFile ? <span>{headerLogoFile.name}</span> : siteSettings.header_logo ? <img src={siteSettings.header_logo} alt="پیش‌نمایش لوگو" style={{width:siteSettings.header_logo_width,maxHeight:70,objectFit:"contain"}}/> : <strong>{siteSettings.site_title}</strong>}</div>
      </div>
      <div className="admin-custom-tabs"><h3>شخصی‌سازی سه بخش اصلی سایت</h3><p className="muted small-text">تنظیمات سربرگ، پابرگ و صفحه اصلی جداگانه نگهداری می‌شوند. برای هر بخش می‌توان متن‌ها، رنگ‌ها و گزینه‌های ظاهری را تعریف کرد.</p>
        <div className="site-settings-grid">
          <label className="wide-field">تنظیمات سربرگ (ساختار JSON)<textarea rows={4} dir="ltr" value={JSON.stringify(siteSettings.header_custom||{},null,2)} onChange={e=>{try{const v=JSON.parse(e.target.value);setSiteSettings(o=>o?{...o,header_custom:v}:o)}catch{}}}/></label>
          <label className="wide-field">تنظیمات پابرگ (ساختار JSON)<textarea rows={4} dir="ltr" value={JSON.stringify(siteSettings.footer_custom||{},null,2)} onChange={e=>{try{const v=JSON.parse(e.target.value);setSiteSettings(o=>o?{...o,footer_custom:v}:o)}catch{}}}/></label>
          <label className="wide-field">تنظیمات صفحه اصلی (ساختار JSON)<textarea rows={4} dir="ltr" value={JSON.stringify(siteSettings.home_custom||{},null,2)} onChange={e=>{try{const v=JSON.parse(e.target.value);setSiteSettings(o=>o?{...o,home_custom:v}:o)}catch{}}}/></label>
        </div>
        <div className="font-upload-box"><strong>قلم اختصاصی سایت</strong>{siteSettings.custom_font&&<p className="muted small-text">قلم فعال: {siteSettings.custom_font_name||"قلم بارگذاری‌شده"}</p>}<input id="custom-font-file" className="visually-hidden-file" type="file" accept=".woff2,.woff,.ttf,.otf" onChange={e=>setFontFile(e.target.files?.[0]||null)}/><label htmlFor="custom-font-file" className="button button-outline button-small">انتخاب پرونده قلم</label><span>{fontFile ? `قلم انتخاب‌شده: ${fontFile.name}` : "فرمت‌های WOFF2، WOFF، TTF و OTF"}</span></div>
      </div>
      <div className="site-settings-grid">
        <label>حداکثر تعداد واژه‌های هر پست (۱۰ تا ۵۰۰۰)
          <input type="number" min={10} max={5000} value={siteSettings.post_max_words ?? 500} onChange={e=>setSiteSettings(old=>old?{...old,post_max_words:Number(e.target.value)}:old)}/>
        </label>
        <p className="muted small-text">مقدار پیش‌فرض ۵۰۰ واژه است و محدودیت در سمت سرور نیز کنترل می‌شود.</p>
      </div>
      <div className="site-settings-grid nav-settings-grid">
        <label>پس‌زمینه منوی پایین<input type="color" value={siteSettings.bottom_nav_background||"#ffffff"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_background:e.target.value}:old)}/></label>
        <label>رنگ آیکون‌ها<input type="color" value={siteSettings.bottom_nav_color||"#7b8297"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_color:e.target.value}:old)}/></label>
        <label>رنگ گزینه فعال<input type="color" value={siteSettings.bottom_nav_active_color||"#34479D"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_active_color:e.target.value}:old)}/></label>
        <label>عنوان خانه<input value={siteSettings.bottom_nav_home_label||"خانه"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_home_label:e.target.value}:old)}/></label>
        <label>عنوان اکسپلور<input value={siteSettings.bottom_nav_explore_label||"اکسپلور"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_explore_label:e.target.value}:old)}/></label>
        <label>عنوان برای شما<input value={siteSettings.bottom_nav_following_label||"برای شما"} onChange={e=>setSiteSettings(old=>old?{...old,bottom_nav_following_label:e.target.value}:old)}/></label>
      </div>
      <div className="site-settings-grid">
        {([ ["site_title", "عنوان سایت"], ["hero_title", "تیتر اصلی"], ["hero_highlight", "ادامه تیتر"], ["feed_title", "عنوان نوشته‌ها"], ["about_title", "عنوان درباره ما"], ["features_title", "عنوان امکانات"], ["footer_text", "متن پابرگ"] ] as const).map(([key, label]) => <label key={key}>{label}<input value={siteSettings[key]} onChange={e => setSiteSettings(old => old ? { ...old, [key]: e.target.value } : old)} /></label>)}
        <label className="wide-field">توضیح بخش معرفی<textarea rows={3} value={siteSettings.hero_description} onChange={e => setSiteSettings(old => old ? { ...old, hero_description: e.target.value } : old)} /></label>
        <label className="wide-field">متن درباره ما<textarea rows={3} value={siteSettings.about_text} onChange={e => setSiteSettings(old => old ? { ...old, about_text: e.target.value } : old)} /></label>
        <label className="wide-field">امکانات (هر مورد در یک خط)<textarea rows={4} value={siteSettings.features_text} onChange={e => setSiteSettings(old => old ? { ...old, features_text: e.target.value } : old)} /></label>
      </div>
      <div className="admin-toggle-row">{([ ["show_hero", "نمایش معرفی"], ["show_about", "نمایش درباره ما"], ["show_features", "نمایش امکانات"], ["show_join", "دعوت به عضویت"] ] as const).map(([key, label]) => <label key={key}><input type="checkbox" checked={siteSettings[key]} onChange={e => setSiteSettings(old => old ? { ...old, [key]: e.target.checked } : old)} /> {label}</label>)}</div>
      {settingsMessage && <p className="notice-bar">{settingsMessage}</p>}
      <button className="button button-primary" onClick={async () => { try { const saved = await apiFetch<SiteSettings>("/api/admin/site-settings/", { method: "PATCH", body: JSON.stringify(siteSettings) }); let finalSettings = saved; if (headerLogoFile || fontFile) { const form = new FormData(); if(headerLogoFile) form.append("header_logo", headerLogoFile); if(fontFile) { form.append("custom_font", fontFile); form.append("custom_font_name", fontFile.name.replace(/\.[^.]+$/, "").replace(/[^\p{L}\p{N}_-]+/gu, "-").slice(0,80)); } form.append("header_logo_width", String(siteSettings.header_logo_width)); form.append("header_logo_position", siteSettings.header_logo_position); form.append("header_background", siteSettings.header_background); finalSettings = await apiFetch<SiteSettings>("/api/admin/site-settings/", {method:"PATCH",body:form}); setHeaderLogoFile(null); setFontFile(null); } setSiteSettings(finalSettings); setSettingsMessage("تنظیمات و سربرگ سایت ذخیره شد."); window.dispatchEvent(new Event("if-site-settings-updated")); } catch (e) { setSettingsMessage(e instanceof Error ? e.message : "ذخیره انجام نشد."); } }}>ذخیره تغییرات سایت</button>
    </div></details>}



    <details className="admin-section admin-collapsible"><summary><span><strong>مدیریت کاربران</strong><small>{users.length} کاربر در فهرست فعلی</small></span><b>مشاهده کاربران</b></summary><div className="admin-collapsible-body"><span className="muted small-text">{users.length} نتیجه (حداکثر ۵۰ مورد)</span>
      <div className="admin-user-search"><input value={userSearch} onChange={e=>setUserSearch(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")void load();}} placeholder="جست‌وجوی نام کاربری، نام یا ایمیل..."/><button className="button button-outline button-small" onClick={load}>جست‌وجو</button></div>
      <div className="table-wrap"><table><thead><tr><th>کاربر</th><th>ایمیل</th><th>وضعیت</th><th>عملیات</th></tr></thead><tbody>
        {users.map((item) => <tr key={item.id}><td><label className="user-select"><input type="checkbox" checked={selectedUsers.includes(item.id)} onChange={(event) => setSelectedUsers((old) => event.target.checked ? [...old, item.id] : old.filter((id) => id !== item.id))} /><span><strong>{item.display_name || item.username}</strong><small>@{item.username}</small></span></label></td><td>{item.email}</td><td>{item.is_suspended ? "تعلیق‌شده" : "فعال"} {item.is_verified && "· تأییدشده"}</td><td className="table-actions"><button onClick={() => userAction(item.id, "verify")}>{item.is_verified ? "لغو نشان" : "نشان تأیید"}</button><button onClick={() => userAction(item.id, "suspend")}>{item.is_suspended ? "رفع تعلیق" : "تعلیق"}</button></td></tr>)}
      </tbody></table></div>
    </div></details>

    <details className="admin-section admin-collapsible"><summary><span><strong>ارسال اعلان به کاربران</strong><small>ارسال پیام به کاربران انتخاب‌شده یا همه</small></span><b>نوشتن اعلان</b></summary><div className="admin-collapsible-body">
      <div className="form-stack admin-notice-form notification-admin-card">
        <label>متن اعلان<textarea value={notificationText} onChange={(event) => setNotificationText(event.target.value)} rows={3} maxLength={255} placeholder="متن متن اعلان موردنظر را بنویسید..." /></label>
        <label className="checkbox-label"><input type="checkbox" checked={sendToAll} onChange={(event) => setSendToAll(event.target.checked)} /> ارسال برای همه کاربران</label>
        <p className="muted small-text">برای ارسال به افراد مشخص، ابتدا کاربران را در فهرست مدیریت کاربران انتخاب کنید. تعداد انتخاب‌شده: {selectedUsers.length.toLocaleString("fa-IR")}</p>
        <button className="button button-primary" onClick={sendNotification} disabled={!notificationText.trim() || (!sendToAll && selectedUsers.length === 0)}>ارسال اعلان</button>
      </div>
    </div></details>

    <details className="admin-section admin-collapsible" open><summary><span><strong>مدیریت نوشته‌ها</strong><small>{posts.length} نوشته اخیر؛ برای مشاهده کامل هر نوشته وارد صفحه آن شو</small></span><b>فهرست نوشته‌ها</b></summary><div className="admin-collapsible-body"><span className="muted small-text">{posts.length} پست اخیر</span>
      <div className="table-wrap"><table><thead><tr><th>شناسه</th><th>نویسنده</th><th>محتوا</th><th>وضعیت</th><th>عملیات</th></tr></thead><tbody>
        {posts.map((item) => <tr key={item.id}><td>{item.id}</td><td>@{item.author__username}</td><td className="content-cell"><Link className="admin-post-summary" href={`/post/${item.id}`} title="مشاهده نوشته کامل">{(item.content || "نوشته دارای رسانه").slice(0, 110)}{(item.content || "").length > 110 ? "…" : ""}<small>مشاهده نوشته کامل ←</small></Link></td><td>{item.is_hidden ? "مخفی" : "نمایش"}</td><td className="table-actions"><button onClick={() => postAction(item.id, "hide")}>{item.is_hidden ? "نمایش" : "مخفی‌سازی"}</button><button className="danger-text" onClick={() => setPendingConfirm({kind:"post",id:item.id})}>حذف</button></td></tr>)}
      </tbody></table></div>
    </div></details>

    <details className="admin-section admin-collapsible"><summary><span><strong>مدیریت ارتباط‌ها</strong><small>{follows.length} ارتباط اخیر میان کاربران</small></span><b>مشاهده ارتباط‌ها</b></summary><div className="admin-collapsible-body"><span className="muted small-text">{follows.length} رابطه اخیر</span>
      <div className="table-wrap"><table><thead><tr><th>دنبال‌کننده</th><th>دنبال‌شونده</th><th>عملیات</th></tr></thead><tbody>
        {follows.map((item) => <tr key={item.id}><td>@{item.follower__username}</td><td>@{item.following__username}</td><td><button onClick={() => setPendingConfirm({kind:"follow",id:item.id})}>حذف رابطه</button></td></tr>)}
      </tbody></table></div>
    </div></details>

    <details className="admin-section admin-collapsible"><summary><span><strong>گزارش‌های کاربران</strong><small>{reports.filter(item => !item.is_resolved).length} گزارش در انتظار رسیدگی</small></span><b>بررسی گزارش‌ها</b></summary><div className="admin-collapsible-body">
      <div className="table-wrap"><table><thead><tr><th>شناسه</th><th>گزارش‌دهنده</th><th>پست</th><th>دلیل</th><th>وضعیت</th><th></th></tr></thead><tbody>
        {reports.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.reporter__username || "کاربر حذف‌شده"}</td><td>{item.post_id}</td><td>{item.reason}</td><td>{item.is_resolved ? "رسیدگی‌شده" : "باز"}</td><td>{!item.is_resolved && <button onClick={() => resolveReport(item.id)}>ثبت رسیدگی</button>}</td></tr>)}
      </tbody></table></div>
    </div></details>
    {pendingConfirm && <div className="confirm-backdrop" role="presentation"><section className="confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title"><h2 id="confirm-title">تأیید عملیات</h2><p>{pendingConfirm.kind === "post" ? "این نوشته برای همیشه حذف شود؟" : "این ارتباط دنبال‌کردن حذف شود؟"}</p><div><button className="button button-danger" onClick={async()=>{const action=pendingConfirm;setPendingConfirm(null);if(action.kind==="post")await postAction(action.id,"delete");else await removeFollow(action.id);}}>بله، حذف شود</button><button className="button button-outline" onClick={()=>setPendingConfirm(null)}>انصراف</button></div></section></div>}
    <p className="muted small-text">برای تنظیمات کامل‌تر، پنل اصلی مدیریت نیز از مسیر <code dir="ltr">/admin/</code> در دسترس است.</p>
  </div>;
}

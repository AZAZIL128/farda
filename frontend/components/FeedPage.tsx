"use client";

// صفحه اصلی: معرفی رسانه ایران فردا، فرم انتشار پست و فید کاربران.
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { apiFetch } from "@/lib/api";
import type { Paginated, Post } from "@/lib/types";
import { useAuth } from "@/components/AuthProvider";
import PostCard from "@/components/PostCard";

export default function FeedPage({ feed = "home" }: { feed?: "home" | "following" | "explore" }) {
  const { user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const [site, setSite] = useState<any>(null);
  const [prefs, setPrefs] = useState<any>(null);
  const [nextPage, setNextPage] = useState<number | null>(2);
  const [moreLoading, setMoreLoading] = useState(false);

  useEffect(() => {
    apiFetch<any>("/api/site-settings/").then(setSite).catch(() => setSite(null));
  }, []);
  useEffect(() => {
    if (user) apiFetch<any>("/api/auth/preferences/").then(setPrefs).catch(() => setPrefs(null));
    else setPrefs(null);
  }, [user]);

  // دریافت فید عمومی پست‌ها از API جنگو
  const loadPosts = useCallback(async () => {
    setLoading(true);
    try {
      const endpoint = feed === "following" ? "/api/posts/?feed=following" : feed === "explore" ? "/api/posts/?feed=explore" : "/api/posts/?sort=popular";
      const data = await apiFetch<Paginated<Post>>(endpoint);
      setPosts(data.results || []);
      setNextPage(data.next ? 2 : null);
    } catch { setNotice("دریافت فید با خطا روبه‌رو شد؛ اتصال سرویس‌ها را بررسی کنید."); }
    finally { setLoading(false); }
  }, [feed]);

  const loadMore = useCallback(async () => {
    if (!nextPage || moreLoading) return;
    setMoreLoading(true);
    try {
      const base = feed === "following" ? "feed=following" : feed === "explore" ? "feed=explore" : "sort=popular";
      const data = await apiFetch<Paginated<Post>>(`/api/posts/?${base}&page=${nextPage}`);
      setPosts(old => [...old, ...(data.results || [])]);
      setNextPage(data.next ? nextPage + 1 : null);
    } catch { setNotice("دریافت ادامه نوشته‌ها ناموفق بود."); }
    finally { setMoreLoading(false); }
  }, [feed, nextPage, moreLoading]);

  useEffect(() => { void loadPosts(); }, [loadPosts]);
  useEffect(() => {
    let previous = window.scrollY;
    let lastRefresh = 0;
    const onScroll = () => {
      const current = window.scrollY;
      if (previous > 120 && current < 12 && Date.now() - lastRefresh > 1800) {
        lastRefresh = Date.now();
        void loadPosts();
      }
      previous = current;
    };
    window.addEventListener("scroll", onScroll, {passive:true});
    return () => window.removeEventListener("scroll", onScroll);
  }, [loadPosts]);
  useEffect(() => {
    const marker = document.getElementById("feed-load-more");
    if (!marker || !nextPage) return;
    const observer = new IntersectionObserver(entries => { if (entries[0]?.isIntersecting) void loadMore(); }, {rootMargin:"500px"});
    observer.observe(marker);
    return () => observer.disconnect();
  }, [nextPage, loadMore]);


  return (
    <div className="page-shell">
      <button className="refresh-fab" type="button" aria-label="تازه‌سازی صفحه" title="تازه‌سازی" onClick={()=>{window.scrollTo({top:0,behavior:"smooth"});void loadPosts();}}><svg viewBox="0 0 24 24"><path d="M20 7v5h-5M4 17v-5h5M5.6 9a7 7 0 0 1 11.8-2L20 12M4 12l2.6 5a7 7 0 0 0 11.8-2"/></svg></button>
      {(!prefs || prefs.show_hero) && (!site || site.show_hero) && <section className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow">رسانه معلمان ایران</span>
          <h1>{site?.hero_title || "صدای جامعه معلمان،"} <span>{site?.hero_highlight || "برای فردای بهتر"}</span></h1>
          <p>{site?.hero_description || "ایران فردا فضایی برای گفتگو، انتشار تجربه‌ها، هم‌اندیشی و ارتباط میان معلمان و فعالان آموزشی است."}</p>
          <div className="hero-buttons">
            {!user && <><Link className="button button-primary" href="/register">عضویت در ایران فردا</Link><Link className="button button-outline" href="/login">ورود به حساب</Link></>}
          </div>
          <div className="hero-note"><span className="gold-dot" /> جامعه‌ای برای یادگیری و هم‌افزایی</div>
        </div>
        <div className="hero-brand-card">
          <Image src="/logo-symbol.png" alt="نشان ایران فردا" width={260} height={260} className="hero-symbol" priority />
          <div className="brand-card-line" />
          <strong>رسانه معلمان ایران</strong>
          <span>با هم برای آینده آموزش</span>
        </div>
      </section>}

      <section className={`content-layout ${prefs?.compact_feed ? "compact-feed" : ""}`} id="feed">
        <div className="feed-column">
          <div className="section-heading">
            <div><span className="eyebrow">گفتگوهای جامعه</span><h2>{feed === "home" ? "پست‌های برتر" : feed === "following" ? "برای شما" : "اکسپلور؛ چهار روز اخیر"}</h2></div>

          </div>


          {notice && <p className="notice-bar">{notice}</p>}
          {loading ? <div className="empty-state">در حال دریافت نوشته‌ها...</div> : posts.length === 0 ? <div className="empty-state"><strong>هنوز نوشته‌ای منتشر نشده است.</strong><span>اولین نفری باشید که تجربه یا دیدگاه خود را با جامعه به اشتراک می‌گذارد.</span></div> : <div className="post-list">{posts.map((post) => <PostCard key={post.id} post={post} onChanged={loadPosts} />)}</div>}
          {!loading && nextPage && <div id="feed-load-more" className="feed-more">{moreLoading ? "در حال دریافت نوشته‌های بعدی..." : "برای مشاهده ادامه، صفحه را پایین ببرید"}</div>}
        </div>

        {(!prefs || prefs.show_sidebar) && <aside className="sidebar-column">
          {(!prefs || prefs.show_about) && (!site || site.show_about) && <div className="sidebar-card about-card"><h3>{site?.about_title || "درباره ایران فردا"}</h3><p>{site?.about_text || "این فضا برای شنیده‌شدن دیدگاه‌ها، تبادل تجربه و شکل‌گیری ارتباط‌های حرفه‌ای در جامعه آموزشی ایجاد شده است."}</p><div className="sidebar-accent" /></div>}
          {(!prefs || prefs.show_features) && (!site || site.show_features) && <div className="sidebar-card"><h3>{site?.features_title || "قابلیت‌های جامعه"}</h3><ul className="feature-list">{(site?.features_text || "انتشار تجربه و محتوای آموزشی\nگفتگو و تبادل نظر\nدنبال‌کردن همکاران\nدسترسی به پروفایل و اعلان‌ها").split("\n").filter(Boolean).map((item: string, index: number) => <li key={index}>{item}</li>)}</ul></div>}
          {(!site || site.show_join) && !user && <div className="sidebar-join"><Image src="/logo-symbol.png" width={64} height={64} alt="نشان ایران فردا"/><strong>به جمع ایران فردا بپیوندید</strong><span>حساب خود را بسازید و در گفتگوها مشارکت کنید.</span><Link href="/register" className="button button-gold">ایجاد حساب کاربری</Link></div>}
        </aside>}
      </section>
    </div>
  );
}

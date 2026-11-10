"use client";

// صفحه پروفایل عمومی کاربران؛ آمار، توضیحات و نوشته‌های فرد را نمایش می‌دهد.
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { Paginated, Post, User } from "@/lib/types";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import PostCard from "@/components/PostCard";

export default function ProfilePage() {
  const params = useParams<{ username: string }>();
  const username = params.username;
  const { user } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [following, setFollowing] = useState(false);
  const [error, setError] = useState("");

  // دریافت مشخصات عمومی کاربر و پست‌های او
  useEffect(() => {
    const load = async () => {
      try {
        const p = await apiFetch<User>(`/api/auth/users/${encodeURIComponent(username)}/`);
        setProfile(p);
        const data = await apiFetch<Paginated<Post>>(`/api/posts/?username=${encodeURIComponent(username)}`);
        setPosts(data.results || []);
        if (user && user.username !== username) {
          const state = await apiFetch<{ following: boolean }>(`/api/users/${encodeURIComponent(username)}/follow-status/`);
          setFollowing(state.following);
        }
      } catch (err) { setError(err instanceof Error ? err.message : "پروفایل پیدا نشد."); }
    };
    void load();
  }, [username, user]);

  // دنبال‌کردن یا لغو دنبال‌کردن کاربر
  const toggleFollow = async () => {
    if (!user) return setError("برای دنبال‌کردن ابتدا وارد حساب شوید.");
    try {
      const result = await apiFetch<{ following: boolean; followers_count: number }>(`/api/users/${encodeURIComponent(username)}/follow/`, { method: "POST" });
      setFollowing(result.following);
      if (profile) setProfile({ ...profile, followers_count: result.followers_count });
    } catch (err) { setError(err instanceof Error ? err.message : "عملیات دنبال‌کردن انجام نشد."); }
  };

  if (error && !profile) return <div className="page-shell"><div className="empty-state">{error}</div></div>;
  if (!profile) return <div className="page-shell"><div className="empty-state">در حال دریافت پروفایل...</div></div>;

  return <div className="page-shell profile-layout">
    <section className="profile-card">
      <div className="profile-cover" role="img" aria-label="تصویر جلد نمایه" style={profile.cover ? { backgroundImage: `url(${profile.cover})` } : undefined}>{!profile.cover&&<span>نمایه کاربر</span>}</div>
      <div className="profile-main">
        <div className="profile-avatar">{profile.avatar ? <img src={profile.avatar} alt="تصویر پروفایل" onError={e=>{e.currentTarget.style.display="none";e.currentTarget.parentElement?.setAttribute("data-fallback",(profile.display_name||profile.username).slice(0,1));}} /> : (profile.display_name || profile.username).slice(0, 1)}</div>
        <div className="profile-title"><h1>{profile.display_name || profile.username} {profile.is_verified && <span className="verified-mark">✓</span>}</h1><span className="muted">@{profile.username}</span></div>
        {user?.username !== username && <button className={following ? "button button-outline" : "button button-primary"} onClick={toggleFollow}>{following ? "دنبال می‌کنید" : "دنبال‌کردن"}</button>}
      </div>
      {profile.bio && <p className="profile-bio">{profile.bio}</p>}
      <div className="profile-stats"><div><strong>{profile.posts_count ?? posts.length}</strong><span>نوشته</span></div><div><strong>{profile.followers_count ?? 0}</strong><span>دنبال‌کننده</span></div><div><strong>{profile.following_count ?? 0}</strong><span>دنبال‌شونده</span></div></div>
    </section>
    {error && <div className="notice-bar">{error}</div>}
    <div className="section-heading"><h2>نوشته‌های {profile.display_name || profile.username}</h2><Link href="/" className="muted small-text">بازگشت به خانه</Link></div>
    {posts.length ? <div className="post-list">{posts.map((post) => <PostCard key={post.id} post={post} />)}</div> : <div className="empty-state">هنوز نوشته‌ای منتشر نشده است.</div>}
  </div>;
}

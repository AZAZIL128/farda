// نوع داده‌های مشترک برای هماهنگی رابط کاربری با API جنگو
export type User = {
  id: number;
  username: string;
  email?: string;
  display_name?: string;
  bio?: string;
  avatar?: string | null;
  cover?: string | null;
  is_verified?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  followers_count?: number;
  following_count?: number;
  posts_count?: number;
};

export type Post = {
  id: number;
  author: User;
  content: string;
  image: string | null;
  video?: string | null;
  repost_of?: number | null;
  is_bookmarked?: boolean;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
  views_count: number;
  created_at: string;
};

export type Paginated<T> = { count: number; next: string | null; previous: string | null; results: T[] };

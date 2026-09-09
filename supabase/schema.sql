-- 미지의 CCAF 노트 — 진도(답·메모) 저장 테이블.
-- Supabase 대시보드 → SQL Editor 에 붙여 넣고 Run.
-- 로그인한 사용자가 자기 행만 읽고 쓰도록 RLS 를 건다.

create table if not exists public.progress (
  user_id    uuid        not null references auth.users (id) on delete cascade,
  page_id    text        not null,
  data       jsonb       not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id, page_id)
);

alter table public.progress enable row level security;

drop policy if exists "own rows select" on public.progress;
drop policy if exists "own rows insert" on public.progress;
drop policy if exists "own rows update" on public.progress;
drop policy if exists "own rows delete" on public.progress;

create policy "own rows select" on public.progress for select using (auth.uid() = user_id);
create policy "own rows insert" on public.progress for insert with check (auth.uid() = user_id);
create policy "own rows update" on public.progress for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows delete" on public.progress for delete using (auth.uid() = user_id);

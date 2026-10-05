create table if not exists users (
  telegram_id bigint primary key,
  plan text not null default 'free',
  created_at timestamptz not null default now()
);

create table if not exists scans (
  id uuid primary key,
  telegram_id bigint not null references users(telegram_id) on delete cascade,
  chain text not null,
  contract_address text not null,
  risk_score integer,
  created_at timestamptz not null default now()
);

create table if not exists watchlist (
  id uuid primary key,
  telegram_id bigint not null references users(telegram_id) on delete cascade,
  chain text not null,
  contract_address text not null,
  symbol text,
  name text,
  last_price numeric,
  last_liquidity numeric,
  last_volume numeric,
  avg_volume numeric,
  created_at timestamptz not null default now(),
  unique (telegram_id, chain, contract_address)
);

create table if not exists alerts (
  id uuid primary key,
  telegram_id bigint not null references users(telegram_id) on delete cascade,
  watchlist_id uuid references watchlist(id) on delete set null,
  alert_type text not null,
  message text not null,
  created_at timestamptz not null default now()
);

create table if not exists admin_logs (
  id uuid primary key,
  level text not null,
  message text not null,
  created_at timestamptz not null default now()
);

create index if not exists scans_user_created_idx on scans (telegram_id, created_at);
create index if not exists watchlist_user_idx on watchlist (telegram_id);
create index if not exists alerts_user_created_idx on alerts (telegram_id, created_at);

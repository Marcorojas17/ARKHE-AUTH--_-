-- Schema base multi-tenant con RLS
create extension if not exists "pgcrypto";

create table if not exists companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists folios (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references companies(id) on delete cascade,
  folio text not null unique,
  payload_hash text not null,
  created_at timestamptz not null default now()
);
create index if not exists folios_company_idx on folios(company_id);

alter table folios enable row level security;
-- Política ejemplo — ajustar cuando exista auth real
create policy folios_company_isolation on folios
  for all using (company_id = current_setting('app.company_id', true)::uuid);

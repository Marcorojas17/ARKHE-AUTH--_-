# database/ — DEPRECADO

Fuente de verdad: `infra/supabase/migrations/`.

Razón: Supabase es el runtime real. Tener migraciones en dos lados
genera drift garantizado. Este directorio solo existe por compatibilidad
histórica y debe quedar vacío.

Para regenerar un dump:

    supabase db dump --schema public > /tmp/schema.sql

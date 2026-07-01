-- ============================================================
-- KIKOCAR — Migración v3
-- 1. Agregar horas_estimadas a ordenes_servicio
-- 2. Reemplazar galones_combustible + costo por galones_inicial/final
-- ============================================================

ALTER TABLE ordenes_servicio
    ADD COLUMN IF NOT EXISTS horas_estimadas NUMERIC(10,2) NOT NULL DEFAULT 240;

ALTER TABLE reportes_diarios
    ADD COLUMN IF NOT EXISTS galones_inicial NUMERIC(10,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS galones_final   NUMERIC(10,2) NOT NULL DEFAULT 0;

-- Los campos viejos los dejamos para no romper datos existentes,
-- pero el código nuevo usará galones_inicial y galones_final.
-- Opcional: renombrar viejos si se quiere limpiar:
-- ALTER TABLE reportes_diarios RENAME COLUMN galones_combustible TO galones_combustible_old;
-- ALTER TABLE reportes_diarios RENAME COLUMN costo_combustible TO costo_combustible_old;

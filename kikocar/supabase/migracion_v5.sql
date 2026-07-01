-- ============================================================
-- KIKOCAR — Migración v5
-- 1. Agregar horometro_ingreso a ordenes_servicio
-- ============================================================

ALTER TABLE ordenes_servicio
    ADD COLUMN IF NOT EXISTS horometro_ingreso NUMERIC(10,2);

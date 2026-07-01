-- ============================================================
-- KIKOCAR — Migración v4
-- 1. fallas_reportadas + requiere_atencion en reportes_diarios
-- 2. Tabla mantenimientos + columna notas_mant en maquinaria
-- ============================================================

ALTER TABLE reportes_diarios
    ADD COLUMN IF NOT EXISTS fallas_reportadas TEXT,
    ADD COLUMN IF NOT EXISTS requiere_atencion BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE maquinaria
    ADD COLUMN IF NOT EXISTS notas_mantenimiento TEXT;

CREATE TABLE IF NOT EXISTS mantenimientos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    maquina_id      UUID          NOT NULL REFERENCES maquinaria(id),
    orden_id        UUID          REFERENCES ordenes_servicio(id),
    fecha           DATE          NOT NULL DEFAULT CURRENT_DATE,
    horometro_actual NUMERIC(10,2) NOT NULL,
    tipo            VARCHAR(50)   NOT NULL DEFAULT 'PREVENTIVO'
                    CHECK (tipo IN ('PREVENTIVO','CORRECTIVO','PREDICTIVO')),
    descripcion     TEXT,
    costo           NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ   DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mantenimientos_maquina ON mantenimientos(maquina_id);

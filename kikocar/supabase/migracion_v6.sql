-- ============================================================
-- KIKOCAR — Migracion v6: Horometros reales de flota
-- Ejecutar en SQL Editor de Supabase
-- ============================================================

-- Terex AC 90 (TRX-090A): 1850 h, ultimo mant a 1700 h (150h de uso)
UPDATE maquinaria
SET horometro_actual = 1850.00,
    ultimo_mant_horas = 1700.00
WHERE codigo_interno = 'TRX-090A';

-- Terex RT 90 (TRX-090B): 2130 h, ultimo mant a 2000 h (130h de uso)
UPDATE maquinaria
SET horometro_actual = 2130.00,
    ultimo_mant_horas = 2000.00
WHERE codigo_interno = 'TRX-090B';

-- Zoomlion ZTC1100V (ZLM-110A): 250 h, ultimo mant a 0 h (250h de uso = vencido)
UPDATE maquinaria
SET horometro_actual = 250.00,
    ultimo_mant_horas = 0.00
WHERE codigo_interno = 'ZLM-110A';

-- Zoomlion ZTC1300V (ZLM-130A): 320 h, ultimo mant a 250 h (70h de uso)
UPDATE maquinaria
SET horometro_actual = 320.00,
    ultimo_mant_horas = 250.00
WHERE codigo_interno = 'ZLM-130A';

-- Zoomlion ZCC300 (ZLM-300A): 155 h, ultimo mant a 0 h (155h de uso)
UPDATE maquinaria
SET horometro_actual = 155.00,
    ultimo_mant_horas = 0.00
WHERE codigo_interno = 'ZLM-300A';

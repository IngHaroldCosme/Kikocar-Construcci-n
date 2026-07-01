-- ============================================================
-- KIKOCAR CONSTRUCCIÓN — Esquema Supabase (PostgreSQL)
-- Ejecutar en el SQL Editor de Supabase
-- ============================================================

-- LIMPIEZA (orden inverso de dependencias)
DROP TABLE IF EXISTS reportes_diarios CASCADE;
DROP TABLE IF EXISTS ordenes_servicio CASCADE;
DROP TABLE IF EXISTS maquinaria CASCADE;
DROP TABLE IF EXISTS operadores CASCADE;
DROP TABLE IF EXISTS frentes_obra CASCADE;

-- ======================= TABLAS =======================

CREATE TABLE frentes_obra (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(150)  NOT NULL,
    ubicacion   VARCHAR(255)  NOT NULL,
    cliente     VARCHAR(150)  NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT now()
);

CREATE TABLE operadores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dni         VARCHAR(15)   NOT NULL UNIQUE,
    nombre      VARCHAR(100)  NOT NULL,
    apellido    VARCHAR(100)  NOT NULL,
    licencia    VARCHAR(50)   NOT NULL,
    estado      VARCHAR(20)   NOT NULL DEFAULT 'DISPONIBLE'
                    CHECK (estado IN ('DISPONIBLE','ASIGNADO','INACTIVO')),
    created_at  TIMESTAMPTZ   DEFAULT now()
);

CREATE TABLE maquinaria (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_interno      VARCHAR(30)   NOT NULL UNIQUE,
    marca               VARCHAR(100)  NOT NULL,
    modelo              VARCHAR(100)  NOT NULL,
    tipo                VARCHAR(50)   NOT NULL,
    consumo_teorico_gh  NUMERIC(6,2)  NOT NULL,
    horometro_actual    NUMERIC(10,2) NOT NULL DEFAULT 0,
    ultimo_mant_horas   NUMERIC(10,2) NOT NULL DEFAULT 0,
    intervalo_mant_horas NUMERIC(10,2) NOT NULL DEFAULT 250,
    estado_operativo    VARCHAR(20)   NOT NULL DEFAULT 'OPERATIVA'
                    CHECK (estado_operativo IN ('OPERATIVA','EN MANTENIMIENTO','FUERA DE SERVICIO')),
    created_at          TIMESTAMPTZ   DEFAULT now()
);

CREATE TABLE ordenes_servicio (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_orden    VARCHAR(50)   NOT NULL UNIQUE,
    cliente         VARCHAR(150)  NOT NULL,
    descripcion     TEXT,
    monto           NUMERIC(12,2) NOT NULL DEFAULT 0,
    fecha_inicio    DATE          NOT NULL,
    fecha_fin       DATE,
    frente_id       UUID          REFERENCES frentes_obra(id),
    maquina_id      UUID          NOT NULL REFERENCES maquinaria(id),
    operador_id     UUID          NOT NULL REFERENCES operadores(id),
    estado          VARCHAR(20)   NOT NULL DEFAULT 'ACTIVA'
                    CHECK (estado IN ('ACTIVA','EN_PROGRESO','COMPLETADA','CANCELADA')),
    created_at      TIMESTAMPTZ   DEFAULT now()
);

CREATE TABLE reportes_diarios (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orden_id            UUID          NOT NULL REFERENCES ordenes_servicio(id),
    fecha               DATE          NOT NULL DEFAULT CURRENT_DATE,
    horometro_inicio    NUMERIC(10,2) NOT NULL,
    horometro_fin       NUMERIC(10,2) NOT NULL,
    horas_trabajadas    NUMERIC(10,2) NOT NULL,
    galones_combustible NUMERIC(10,2) NOT NULL,
    costo_combustible   NUMERIC(12,2) NOT NULL DEFAULT 0,
    descripcion         TEXT,
    alerta_robo         BOOLEAN       NOT NULL DEFAULT FALSE,
    probabilidad_fallo  NUMERIC(5,2)  DEFAULT 0,
    dias_restantes_mant INT           DEFAULT 0,
    created_at          TIMESTAMPTZ   DEFAULT now()
);

-- ======================= ÍNDICES =======================
CREATE INDEX idx_ordenes_operador ON ordenes_servicio(operador_id);
CREATE INDEX idx_ordenes_maquina  ON ordenes_servicio(maquina_id);
CREATE INDEX idx_reportes_orden   ON reportes_diarios(orden_id);
CREATE INDEX idx_maquinaria_estado ON maquinaria(estado_operativo);

-- ======================= SEED DATA =======================

-- FRENTES DE OBRA
INSERT INTO frentes_obra (nombre, ubicacion, cliente) VALUES
('Edificio Torres del Sol','Av. Principal 1234, Lima','Constructora Los Andes'),
('Puente Grau','Km 14 Panamericana Sur, Ica','Gobierno Regional Ica'),
('Mina Cerro Verde','Carretera Arequipa-Mollendo, Arequipa','Sociedad Minera Cerro Verde'),
('Ampliación Aeropuerto','Av. Elmer Faucett, Callao','Ministerio de Transportes');

-- OPERADORES
INSERT INTO operadores (dni, nombre, apellido, licencia, estado) VALUES
('12345678','Carlos','Gutiérrez','A-IIIB','DISPONIBLE'),
('23456789','María','Fernández','A-IIIC','DISPONIBLE'),
('34567890','José','Ramírez','A-IIIB','DISPONIBLE'),
('45678901','Luis','Torres','A-II','DISPONIBLE'),
('56789012','Ana','Mendoza','A-IIIB','DISPONIBLE');

-- MAQUINARIA — Flota real de 8 grúas
INSERT INTO maquinaria (codigo_interno, marca, modelo, tipo, consumo_teorico_gh, horometro_actual, ultimo_mant_horas, intervalo_mant_horas, estado_operativo) VALUES
('ZLM-001','Zoomlion','ZTC250A','Grúa Móvil',8.50, 4520.00, 4300.00, 250, 'OPERATIVA'),
('ZLM-002','Zoomlion','ZTC350A','Grúa Móvil',10.20, 3890.00, 3650.00, 250, 'OPERATIVA'),
('ZLM-003','Zoomlion','ZTC550V','Grúa Móvil',12.80, 2100.00, 2000.00, 250, 'OPERATIVA'),
('ZLM-004','Zoomlion','QUY80','Grúa Oruga',14.50, 6780.00, 6500.00, 250, 'OPERATIVA'),
('TRX-001','Terex','RT555','Grúa Todoterreno',11.30, 3340.00, 3100.00, 250, 'OPERATIVA'),
('TRX-002','Terex','CC6800','Grúa Oruga',18.70, 12450.00, 12200.00, 250, 'OPERATIVA'),
('TRX-003','Terex','AC100','Grúa Móvil',13.40, 5670.00, 5450.00, 250, 'OPERATIVA'),
('TRX-004','Terex','Demag AC700','Grúa Móvil',15.90, 8900.00, 8700.00, 250, 'OPERATIVA');

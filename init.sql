-- init.sql
CREATE TABLE IF NOT EXISTS modelos_ml (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255),
    descripcion TEXT,
    tipo_modelo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metricas TEXT,
    modelo_binario BYTEA,
    ruta_archivo VARCHAR(255)
);

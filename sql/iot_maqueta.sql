-- Crear la tabla de sensores
CREATE TABLE sensores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(100),
    ubicacion VARCHAR(100),
    responsable VARCHAR(50)
);

-- Insertar sensores registrados
INSERT INTO sensores (nombre, tipo, ubicacion, responsable) VALUES
('Sensor de Gas/Humo', 'MQ2', 'Sala', 'Mane'),
('Sensor Táctil', 'KY-036', 'Entrada', 'Mane'),
('Sensor Temp/Hum', 'KY-015', 'Dormitorio', 'Agustin'),
('Sensor de Flama', 'KY-026', 'Cocina', 'Agustin'),
('Buzzer', 'KY-012', 'Cocina', 'Agustin'),
('Sensor de Luz', 'KY-018', 'Pasillo', 'Meño'),
('Sensor de Proximidad', 'KY-032', 'Pasillo', 'Meño');

-- Crear la tabla de lecturas por sensor
CREATE TABLE lecturas_sensor (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensores(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor TEXT
);

CREATE TABLE IF NOT EXISTS node_telemetry (
    id UUID NOT NULL,
    message_id UUID NOT NULL,
    node_id UUID NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cpu_percent DOUBLE PRECISION NOT NULL,
    memory_percent DOUBLE PRECISION NOT NULL,
    disk_percent DOUBLE PRECISION NOT NULL,

    CONSTRAINT node_telemetry_pkey PRIMARY KEY (id),

    CONSTRAINT uq_node_telemetry_node_message
        UNIQUE (node_id, message_id),

    CONSTRAINT ck_node_telemetry_cpu_percent
        CHECK (cpu_percent >= 0 AND cpu_percent <= 100),

    CONSTRAINT ck_node_telemetry_memory_percent
        CHECK (memory_percent >= 0 AND memory_percent <= 100),

    CONSTRAINT ck_node_telemetry_disk_percent
        CHECK (disk_percent >= 0 AND disk_percent <= 100),

    CONSTRAINT node_telemetry_node_id_fkey
        FOREIGN KEY (node_id)
        REFERENCES nodes(id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS ix_node_telemetry_node_time
ON node_telemetry (node_id, measured_at, received_at, id);
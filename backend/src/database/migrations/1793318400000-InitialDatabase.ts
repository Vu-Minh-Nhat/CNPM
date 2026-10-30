import type { MigrationInterface, QueryRunner } from 'typeorm';

export class InitialDatabase1793318400000 implements MigrationInterface {
  async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      CREATE TABLE roles (
        code varchar(32) PRIMARY KEY,
        name varchar(200) NOT NULL CHECK (btrim(name) <> ''),
        CONSTRAINT roles_code_check CHECK (code IN ('Administrator', 'Operator', 'Technician'))
      );
      INSERT INTO roles (code, name) VALUES
        ('Administrator', 'System Administrator'), ('Operator', 'System Operator'), ('Technician', 'Technician');
      CREATE TABLE users (
        id uuid PRIMARY KEY,
        email varchar(254) NOT NULL CHECK (email = lower(btrim(email)) AND position('@' IN email) > 1),
        password_hash varchar(255) NOT NULL CHECK (password_hash ~ '^\\$2[aby]\\$[0-9]{2}\\$[./A-Za-z0-9]{53}$'),
        role_code varchar(32) NOT NULL REFERENCES roles(code) ON DELETE RESTRICT,
        is_active boolean NOT NULL DEFAULT true,
        created_at timestamptz NOT NULL DEFAULT now(),
        CONSTRAINT users_email_key UNIQUE (email)
      );
      CREATE INDEX users_role_idx ON users(role_code);
      CREATE TABLE sites (
        id uuid PRIMARY KEY,
        code varchar(64) NOT NULL UNIQUE CHECK (btrim(code) <> ''),
        name varchar(200) NOT NULL CHECK (btrim(name) <> '')
      );
      CREATE TABLE rooms (
        id uuid PRIMARY KEY,
        site_id uuid NOT NULL REFERENCES sites(id) ON DELETE RESTRICT,
        code varchar(64) NOT NULL CHECK (btrim(code) <> ''),
        name varchar(200) NOT NULL CHECK (btrim(name) <> ''),
        UNIQUE (site_id, code)
      );
      CREATE TABLE racks (
        id uuid PRIMARY KEY,
        room_id uuid NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
        code varchar(64) NOT NULL CHECK (btrim(code) <> ''),
        name varchar(200) NOT NULL CHECK (btrim(name) <> ''),
        capacity_u integer NOT NULL DEFAULT 42 CHECK (capacity_u > 0 AND capacity_u <= 100),
        UNIQUE (room_id, code)
      );
      CREATE TABLE nodes (
        id uuid PRIMARY KEY,
        rack_id uuid NOT NULL REFERENCES racks(id) ON DELETE RESTRICT,
        code varchar(64) NOT NULL UNIQUE CHECK (btrim(code) <> ''),
        name varchar(200) NOT NULL CHECK (btrim(name) <> ''),
        serial_number varchar(128) UNIQUE CHECK (serial_number IS NULL OR btrim(serial_number) <> '')
      );
      CREATE INDEX nodes_rack_idx ON nodes(rack_id);
      CREATE TABLE workloads (
        id uuid PRIMARY KEY,
        node_id uuid NOT NULL REFERENCES nodes(id) ON DELETE RESTRICT,
        code varchar(64) NOT NULL CHECK (btrim(code) <> ''),
        name varchar(200) NOT NULL CHECK (btrim(name) <> ''),
        runtime_id varchar(200) CHECK (runtime_id IS NULL OR btrim(runtime_id) <> ''),
        UNIQUE (node_id, code),
        UNIQUE (node_id, runtime_id)
      );
    `);
  }

  async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      DROP TABLE workloads;
      DROP TABLE nodes;
      DROP TABLE racks;
      DROP TABLE rooms;
      DROP TABLE sites;
      DROP TABLE users;
      DROP TABLE roles;
    `);
  }
}

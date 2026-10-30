import { EntitySchema } from 'typeorm';
import type { Role } from '../common/enums/role.enum.js';

export interface RoleEntity { code: Role; name: string }
export interface AccountEntity {
  id: string; email: string; passwordHash: string; role: Role;
  isActive: boolean; createdAt: Date; roleDetails?: RoleEntity;
}
export interface SiteEntity { id: string; code: string; name: string; rooms?: RoomEntity[] }
export interface RoomEntity { id: string; siteId: string; code: string; name: string; site?: SiteEntity; racks?: RackEntity[] }
export interface RackEntity { id: string; roomId: string; code: string; name: string; capacityU: number; room?: RoomEntity; nodes?: NodeEntity[] }
export interface NodeEntity { id: string; rackId: string; code: string; name: string; serialNumber: string | null; rack?: RackEntity; workloads?: WorkloadEntity[] }
export interface WorkloadEntity { id: string; nodeId: string; code: string; name: string; runtimeId: string | null; node?: NodeEntity }

const id = { type: 'uuid' as const, primary: true };
const code = { type: 'varchar' as const, length: 64 };
const name = { type: 'varchar' as const, length: 200 };

export const RoleSchema = new EntitySchema<RoleEntity>({
  name: 'Role', tableName: 'roles',
  columns: { code: { type: 'varchar', length: 32, primary: true }, name },
});
export const AccountSchema = new EntitySchema<AccountEntity>({
  name: 'Account', tableName: 'users',
  columns: {
    id, email: { type: 'varchar', length: 254 },
    passwordHash: { name: 'password_hash', type: 'varchar', length: 255, select: false },
    role: { name: 'role_code', type: 'varchar', length: 32 },
    isActive: { name: 'is_active', type: 'boolean', default: true },
    createdAt: { name: 'created_at', type: 'timestamptz', createDate: true },
  },
  relations: { roleDetails: { type: 'many-to-one', target: 'Role', joinColumn: { name: 'role_code', referencedColumnName: 'code' }, nullable: false, onDelete: 'RESTRICT' } },
});
export const SiteSchema = new EntitySchema<SiteEntity>({
  name: 'Site', tableName: 'sites', columns: { id, code, name },
  relations: { rooms: { type: 'one-to-many', target: 'Room', inverseSide: 'site' } },
});
export const RoomSchema = new EntitySchema<RoomEntity>({
  name: 'Room', tableName: 'rooms',
  columns: { id, siteId: { name: 'site_id', type: 'uuid' }, code, name },
  relations: {
    site: { type: 'many-to-one', target: 'Site', joinColumn: { name: 'site_id' }, nullable: false, onDelete: 'RESTRICT' },
    racks: { type: 'one-to-many', target: 'Rack', inverseSide: 'room' },
  },
});
export const RackSchema = new EntitySchema<RackEntity>({
  name: 'Rack', tableName: 'racks',
  columns: { id, roomId: { name: 'room_id', type: 'uuid' }, code, name, capacityU: { name: 'capacity_u', type: 'integer', default: 42 } },
  relations: {
    room: { type: 'many-to-one', target: 'Room', joinColumn: { name: 'room_id' }, nullable: false, onDelete: 'RESTRICT' },
    nodes: { type: 'one-to-many', target: 'Node', inverseSide: 'rack' },
  },
});
export const NodeSchema = new EntitySchema<NodeEntity>({
  name: 'Node', tableName: 'nodes',
  columns: { id, rackId: { name: 'rack_id', type: 'uuid' }, code, name, serialNumber: { name: 'serial_number', type: 'varchar', length: 128, nullable: true } },
  relations: {
    rack: { type: 'many-to-one', target: 'Rack', joinColumn: { name: 'rack_id' }, nullable: false, onDelete: 'RESTRICT' },
    workloads: { type: 'one-to-many', target: 'Workload', inverseSide: 'node' },
  },
});
export const WorkloadSchema = new EntitySchema<WorkloadEntity>({
  name: 'Workload', tableName: 'workloads',
  columns: { id, nodeId: { name: 'node_id', type: 'uuid' }, code, name, runtimeId: { name: 'runtime_id', type: 'varchar', length: 200, nullable: true } },
  relations: { node: { type: 'many-to-one', target: 'Node', joinColumn: { name: 'node_id' }, nullable: false, onDelete: 'RESTRICT' } },
});
export const entities = [RoleSchema, AccountSchema, SiteSchema, RoomSchema, RackSchema, NodeSchema, WorkloadSchema];

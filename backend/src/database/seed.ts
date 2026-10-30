import { randomUUID } from 'node:crypto';
import { hash } from 'bcryptjs';
import type { DataSource } from 'typeorm';
import { ALL_ROLES } from '../common/enums/role.enum.js';
import { AccountSchema, SiteSchema, RoomSchema, RackSchema, NodeSchema, WorkloadSchema } from './entities.js';

export async function seedDevelopment(source: DataSource, password = process.env.SEED_PASSWORD): Promise<void> {
  if (process.env.NODE_ENV === 'production') throw new Error('Development seed is disabled in production.');
  if (!password || password.length < 12 || Buffer.byteLength(password, 'utf8') > 72) {
    throw new Error('Set SEED_PASSWORD to 12–72 UTF-8 bytes (at least 12 characters).');
  }
  const passwordHash = await hash(password, 10);
  await source.transaction(async manager => {
    const emails = ['admin@arimms.local', 'operator@arimms.local', 'tech@arimms.local'];
    for (const [index, role] of ALL_ROLES.entries()) {
      await manager.createQueryBuilder().insert().into(AccountSchema).values({
        id: randomUUID(), email: emails[index], passwordHash, role, isActive: true,
      }).orIgnore().execute();
    }
    const site = await manager.findOneBy(SiteSchema, { code: 'DEMO-SITE' });
    if (site) return; // Re-running seed never overwrites an existing demo tree or user password.
    const siteId = randomUUID(); const roomId = randomUUID(); const rackId = randomUUID(); const nodeId = randomUUID();
    await manager.insert(SiteSchema, { id: siteId, code: 'DEMO-SITE', name: 'Mini Data Center Testbed' });
    await manager.insert(RoomSchema, { id: roomId, siteId, code: 'ROOM-01', name: 'Testbed Room' });
    await manager.insert(RackSchema, { id: rackId, roomId, code: 'RACK-01', name: 'Testbed Rack', capacityU: 42 });
    await manager.insert(NodeSchema, { id: nodeId, rackId, code: 'DEMO-NODE-01', name: 'Testbed Server', serialNumber: null });
    await manager.insert(WorkloadSchema, { id: randomUUID(), nodeId, code: 'DEMO-WORKLOAD-01', name: 'Simulated workload', runtimeId: null });
  });
}

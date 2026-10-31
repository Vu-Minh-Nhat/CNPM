import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    ManyToOne
} from 'typeorm';

import type { Rack } from '../../racks/entities/rack.entity.js';

@Entity('servers')
export class Server {
    @PrimaryGeneratedColumn()
    id: number;

    @Column()
    name: string; // Tên máy chủ

    @Column({ nullable: true })
    ipAddress: string; // Địa chỉ IP (nếu có)

    @Column({ default: 'ACTIVE' })
    status: string; // Trạng thái thiết bị

    // Khai báo thuộc tính 'rack' này để khớp với liên kết bên Rack entity
    @ManyToOne('Rack', (rack: Rack) => rack.servers, { onDelete: 'CASCADE' })
    rack: Rack;
}
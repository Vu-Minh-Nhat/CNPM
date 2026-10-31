import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    ManyToOne,
    OneToMany
} from 'typeorm';

import type { Room } from '../../rooms/entities/room.entity.js';
import type { Server } from '../../servers/entities/server.entity.js';

@Entity('racks')
export class Rack {
    @PrimaryGeneratedColumn()
    id: number;

    @Column()
    name: string; // Tên tủ rack

    @Column({ default: 42 })
    capacityU: number; // Sức chứa U của rack

    // Khai báo thuộc tính 'room' này để khớp với 'rack.room' bên Room entity
    @ManyToOne('Room', (room: Room) => room.racks, { onDelete: 'CASCADE' })
    room: Room;

    @OneToMany('Server', (server: Server) => server.rack)
    servers: Server[];
}
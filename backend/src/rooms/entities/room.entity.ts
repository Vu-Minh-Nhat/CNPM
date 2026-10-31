import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    ManyToOne,
    OneToMany
} from 'typeorm';

import type { Site } from '../../sites/entities/site.entity.js';
import type { Rack } from '../../racks/entities/rack.entity.js'; // Import thêm Rack để nối tầng tiếp theo

@Entity('rooms')
export class Room {
    @PrimaryGeneratedColumn()
    id: number;

    @Column()
    name: string; // Tên phòng máy (Ví dụ: Phòng Server A1)

    @ManyToOne('Site', (site: Site) => site.rooms, { onDelete: 'CASCADE' })
    site: Site;

    @OneToMany('Rack', (rack: Rack) => rack.room)
    racks: Rack[]; // Liên kết 1 Room chứa nhiều Rack
}
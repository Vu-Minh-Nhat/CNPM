import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';
import { Room } from '../../rooms/entities/room.entity.js';

@Entity('sites')
export class Site {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  name: string;

  @Column()
  location: string;

  @Column({ nullable: true })
  description: string;

  @OneToMany(() => Room, (room) => room.site)
  rooms: Room[];
}
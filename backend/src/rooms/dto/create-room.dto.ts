import { IsString, IsNotEmpty, IsUUID } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateRoomDto {
  @ApiProperty({ example: 'uuid-cua-site' })
  @IsUUID()
  @IsNotEmpty()
  siteId: string;

  @ApiProperty({ example: 'ROOM-01' })
  @IsString()
  @IsNotEmpty()
  code: string;

  @ApiProperty({ example: 'Phòng máy chủ tầng 1' })
  @IsString()
  @IsNotEmpty()
  name: string;
}

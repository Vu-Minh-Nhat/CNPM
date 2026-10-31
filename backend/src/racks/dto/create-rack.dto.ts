
import { IsString, IsNotEmpty, IsUUID, IsInt, Min, Max } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateRackDto {
  @ApiProperty({ example: 'uuid-cua-room' })
  @IsUUID()
  @IsNotEmpty()
  roomId: string;

  @ApiProperty({ example: 'RACK-01' })
  @IsString()
  @IsNotEmpty()
  code: string;

  @ApiProperty({ example: 'Rack khu A' })
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty({ example: 42, default: 42 })
  @IsInt()
  @Min(1)
  @Max(100)
  capacityU: number;
}

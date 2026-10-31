import { IsString, IsNotEmpty, IsUUID, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateServerDto {
  @ApiProperty({ example: 'uuid-cua-rack' })
  @IsUUID()
  @IsNotEmpty()
  rackId: string;

  @ApiProperty({ example: 'SRV-01' })
  @IsString()
  @IsNotEmpty()
  code: string;

  @ApiProperty({ example: 'Web Server 01' })
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty({ example: 'SN123456', required: false })
  @IsString()
  @IsOptional()
  serialNumber?: string;
}

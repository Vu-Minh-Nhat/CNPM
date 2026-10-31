import { IsString, IsNotEmpty, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger'; // Nếu dùng Swagger

export class CreateSiteDto {
  @ApiProperty({ example: 'Trung tâm dữ liệu Quận 1' })
  @IsString()
  @IsNotEmpty({ message: 'Tên site không được để trống' })
  name: string;

  @ApiProperty({ example: 'TP. Hồ Chí Minh' })
  @IsString()
  @IsNotEmpty({ message: 'Vị trí không được để trống' })
  location: string;

  @ApiProperty({ example: 'Khu vực máy chủ chính', required: false })
  @IsString()
  @IsOptional()
  description?: string;
}
import { Transform } from 'class-transformer';
import { IsNotEmpty, IsString, MaxLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateSiteDto {
  @ApiProperty({
    example: 'SITE-01',
    maxLength: 64,
  })
  @Transform(({ value }) =>
    typeof value === 'string' ? value.trim() : value,
  )
  @IsString()
  @IsNotEmpty({ message: 'Mã Site không được để trống' })
  @MaxLength(64)
  code: string;

  @ApiProperty({
    example: 'Trung tâm dữ liệu Quận 1',
    maxLength: 200,
  })
  @Transform(({ value }) =>
    typeof value === 'string' ? value.trim() : value,
  )
  @IsString()
  @IsNotEmpty({ message: 'Tên Site không được để trống' })
  @MaxLength(200)
  name: string;
}
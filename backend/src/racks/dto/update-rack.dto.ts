import { PartialType } from '@nestjs/swagger';
import { CreateRackDto } from './create-rack.dto.js';

export class UpdateRackDto extends PartialType(CreateRackDto) {}

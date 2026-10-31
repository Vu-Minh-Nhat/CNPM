import { Controller, Get, Post, Body, Patch, Param, Delete, ParseUUIDPipe, } from '@nestjs/common';
import { RacksService } from './racks.service.js';
import { CreateRackDto } from './dto/create-rack.dto.js';
import { UpdateRackDto } from './dto/update-rack.dto.js';
import { Roles } from '../common/decorators/roles.decorator.js';
import { ALL_ROLES, Role } from '../common/enums/role.enum.js';
import { ApiBearerAuth } from '@nestjs/swagger';

@ApiBearerAuth()
@Controller('racks')
@Roles(...ALL_ROLES)
export class RacksController {
  constructor(private readonly racksService: RacksService) {}

  @Post()
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  create(@Body() createRackDto: CreateRackDto) {
    return this.racksService.create(createRackDto);
  }

  @Get()
  findAll() {
    return this.racksService.findAll();
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.racksService.findOne(id);
  }

  @Patch(':id')
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  update(@Param('id', ParseUUIDPipe) id: string, @Body() updateRackDto: UpdateRackDto) {
    return this.racksService.update(id, updateRackDto);
  }

  @Delete(':id')
  @Roles(Role.ADMINISTRATOR)
  remove(@Param('id', ParseUUIDPipe) id: string) {
    return this.racksService.remove(id);
  }
}

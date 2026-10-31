import { Controller, Get, Post, Body, Patch, Param, Delete, ParseUUIDPipe, } from '@nestjs/common';
import { ServersService } from './servers.service.js';
import { CreateServerDto } from './dto/create-server.dto.js';
import { UpdateServerDto } from './dto/update-server.dto.js';
import { Roles } from '../common/decorators/roles.decorator.js';
import { ALL_ROLES, Role } from '../common/enums/role.enum.js';
import { ApiBearerAuth } from '@nestjs/swagger';

@ApiBearerAuth()
@Controller('servers')
@Roles(...ALL_ROLES)
export class ServersController {
  constructor(private readonly serversService: ServersService) {}

  @Post()
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  create(@Body() createServerDto: CreateServerDto) {
    return this.serversService.create(createServerDto);
  }

  @Get()
  findAll() {
    return this.serversService.findAll();
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.serversService.findOne(id);
  }

  @Patch(':id')
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  update(@Param('id', ParseUUIDPipe) id: string, @Body() updateServerDto: UpdateServerDto) {
    return this.serversService.update(id, updateServerDto);
  }

  @Delete(':id')
  @Roles(Role.ADMINISTRATOR)
  remove(@Param('id', ParseUUIDPipe) id: string) {
    return this.serversService.remove(id);
  }
}

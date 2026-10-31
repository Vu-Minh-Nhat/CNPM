import { Controller, Get, Post, Body, Patch, Param, Delete, ParseUUIDPipe, } from '@nestjs/common';
import { RacksService } from './racks.service.js';
import { CreateRackDto } from './dto/create-rack.dto.js';
import { UpdateRackDto } from './dto/update-rack.dto.js';

@Controller('racks')
export class RacksController {
  constructor(private readonly racksService: RacksService) {}

  @Post()
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
  update(@Param('id', ParseUUIDPipe) id: string, @Body() updateRackDto: UpdateRackDto) {
    return this.racksService.update(id, updateRackDto);
  }

  @Delete(':id')
  remove(@Param('id', ParseUUIDPipe) id: string) {
    return this.racksService.remove(id);
  }
}

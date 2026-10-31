import { Module } from '@nestjs/common';
import { RacksService } from './racks.service.js';
import { RacksController } from './racks.controller.js';

@Module({
  controllers: [RacksController],
  providers: [RacksService],
  exports: [RacksService],
})
export class RacksModule {}
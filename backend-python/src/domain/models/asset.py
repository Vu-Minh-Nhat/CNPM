from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Site:
    id: str
    code: str
    name: str


@dataclass(frozen=True, slots=True)
class Room:
    id: str
    site_id: str
    code: str
    name: str
    site: Site | None


@dataclass(frozen=True, slots=True)
class Rack:
    id: str
    room_id: str
    code: str
    name: str
    capacity_u: int
    room: Room | None


@dataclass(frozen=True, slots=True)
class Workload:
    id: str
    node_id: str
    code: str
    name: str
    runtime_id: str | None


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    rack_id: str
    code: str
    name: str
    serial_number: str | None
    rack: Rack | None
    workloads: tuple[Workload, ...]
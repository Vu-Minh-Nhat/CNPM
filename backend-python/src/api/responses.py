from src.domain.models.asset import Node


def asset_response(node: Node) -> dict:
    rack = node.rack
    room = rack.room if rack else None
    site = room.site if room else None

    site_data = None

    if site is not None:
        site_data = {
            "id": site.id,
            "code": site.code,
            "name": site.name,
        }

    room_data = None

    if room is not None:
        room_data = {
            "id": room.id,
            "siteId": room.site_id,
            "code": room.code,
            "name": room.name,
            "site": site_data,
        }

    rack_data = None

    if rack is not None:
        rack_data = {
            "id": rack.id,
            "roomId": rack.room_id,
            "code": rack.code,
            "name": rack.name,
            "capacityU": rack.capacity_u,
            "room": room_data,
        }

    return {
        "id": node.id,
        "rackId": node.rack_id,
        "code": node.code,
        "name": node.name,
        "serialNumber": node.serial_number,
        "rack": rack_data,
        "workloads": [
            {
                "id": workload.id,
                "nodeId": workload.node_id,
                "code": workload.code,
                "name": workload.name,
                "runtimeId": workload.runtime_id,
            }
            for workload in node.workloads
        ],
    }
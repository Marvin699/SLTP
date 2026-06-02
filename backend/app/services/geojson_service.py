from typing import List
from app.models.point import DeliveryPoint


def points_to_geojson(points: List[DeliveryPoint]) -> dict:
    """将数据库点位列表转换为标准GeoJSON FeatureCollection"""
    features = []
    for pt in points:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [pt.longitude, pt.latitude],
            },
            "properties": {
                "id": pt.id,
                "name": pt.name,
                "type": pt.point_type.value if hasattr(pt.point_type, "value") else pt.point_type,
                "longitude": pt.longitude,
                "latitude": pt.latitude,
                "demand_weight": pt.demand_weight,
                "demand_priority": pt.demand_priority,
                "supply_type": pt.supply_type,
                "note": pt.note,
            },
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }

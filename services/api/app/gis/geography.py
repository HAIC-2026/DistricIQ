from shapely.geometry import MultiPolygon, shape


def validate_features(collection: dict, chamber: str):
    expected = {"house": 51, "senate": 25}[chamber]
    features = collection.get("features", [])
    if len(features) != expected or collection.get("exceededTransferLimit"):
        raise ValueError("Incomplete legislative geography response")
    identifiers = []
    for feature in features:
        properties = feature.get("properties", {})
        number = int(properties[chamber + "_id"])
        identifiers.append(number)
        geom = shape(feature["geometry"])
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"Invalid polygon for {chamber} district {number}")
        if not (
            -180 <= geom.bounds[0] < geom.bounds[2] <= -154 and 18 <= geom.bounds[1] < geom.bounds[3] <= 30
        ):
            raise ValueError("District outside Hawaiʻi")
    if sorted(identifiers) != list(range(1, expected + 1)):
        raise ValueError("District ID coverage is incomplete or duplicated")
    return features


def multipolygon(geom):
    g = shape(geom)
    return MultiPolygon([g]) if g.geom_type == "Polygon" else g

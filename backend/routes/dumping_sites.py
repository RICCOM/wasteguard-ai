# from datetime import datetime

# from flask import Blueprint, jsonify, request
# from geoalchemy2.elements import WKTElement

# from extensions import db
# from models.dumping_site import DumpingSite


# dumping_sites_bp = Blueprint(
#     "dumping_sites",
#     __name__
# )


# @dumping_sites_bp.get("")
# def get_dumping_sites():
#     sites = DumpingSite.query.order_by(
#         DumpingSite.created_at.desc()
#     ).all()

#     return jsonify([
#         site.to_dict()
#         for site in sites
#     ])


# @dumping_sites_bp.get("/<int:site_id>")
# def get_dumping_site(site_id):
#     site = DumpingSite.query.get(site_id)

#     if not site:
#         return jsonify({
#             "error": "Dumping site not found"
#         }), 404

#     return jsonify(site.to_dict())


# @dumping_sites_bp.post("")
# def create_dumping_site():
#     data = request.get_json()

#     required_fields = [
#         "latitude",
#         "longitude"
#     ]

#     for field in required_fields:
#         if field not in data:
#             return jsonify({
#                 "error": f"{field} is required"
#             }), 400

#     latitude = float(data["latitude"])
#     longitude = float(data["longitude"])

#     if not -90 <= latitude <= 90:
#         return jsonify({
#             "error": "Invalid latitude"
#         }), 400

#     if not -180 <= longitude <= 180:
#         return jsonify({
#             "error": "Invalid longitude"
#         }), 400

#     case_id = data.get("case_id")

#     if not case_id:
#         case_id = f"WG-{int(datetime.utcnow().timestamp())}"

#     geometry = WKTElement(
#         f"POINT({longitude} {latitude})",
#         srid=4326
#     )

#     site = DumpingSite(
#         case_id=case_id,
#         latitude=latitude,
#         longitude=longitude,
#         geometry=geometry,
#         area_m2=data.get("area_m2"),
#         waste_probability=data.get(
#             "waste_probability"
#         ),
#         confidence=data.get(
#             "confidence"
#         ),
#         risk_score=data.get(
#             "risk_score"
#         ),
#         risk_level=data.get(
#             "risk_level"
#         ),
#         status=data.get(
#             "status",
#             "DETECTED"
#         ),
#         ai_summary=data.get(
#             "ai_summary"
#         ),
#         first_detected=datetime.utcnow(),
#         last_detected=datetime.utcnow()
#     )

#     db.session.add(site)
#     db.session.commit()

#     return jsonify(site.to_dict()), 201


# @dumping_sites_bp.delete("/<int:site_id>")
# def delete_dumping_site(site_id):
#     site = DumpingSite.query.get(site_id)

#     if not site:
#         return jsonify({
#             "error": "Dumping site not found"
#         }), 404

#     db.session.delete(site)
#     db.session.commit()

#     return jsonify({
#         "message": "Dumping site deleted"
#     })
from datetime import datetime

from flask import Blueprint, jsonify, request
from geoalchemy2.elements import WKTElement
from sqlalchemy import func

from extensions import db
from models.dumping_site import DumpingSite


dumping_sites_bp = Blueprint(
    "dumping_sites",
    __name__,
    url_prefix="/api/dumping-sites"
)


def validate_coordinates(latitude, longitude):
    if not (-90 <= latitude <= 90):
        return False

    if not (-180 <= longitude <= 180):
        return False

    return True


def create_point(latitude, longitude):
    return WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326
    )


# ---------------------------------------------------------
# GET ALL
# ---------------------------------------------------------

@dumping_sites_bp.get("")
def get_dumping_sites():

    sites = (
        DumpingSite.query
        .order_by(DumpingSite.created_at.desc())
        .all()
    )

    return jsonify({
        "count": len(sites),
        "data": [
            site.to_dict()
            for site in sites
        ]
    }), 200


# ---------------------------------------------------------
# GET ONE
# ---------------------------------------------------------

@dumping_sites_bp.get("/<int:site_id>")
def get_dumping_site(site_id):

    site = db.session.get(
        DumpingSite,
        site_id
    )

    if site is None:
        return jsonify({
            "error": "Dumping site not found"
        }), 404

    return jsonify(site.to_dict()), 200


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

@dumping_sites_bp.post("")
def create_dumping_site():

    data = request.get_json(silent=True) or {}

    required_fields = [
        "case_id",
        "latitude",
        "longitude",
        "status"
    ]

    missing = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
    except (TypeError, ValueError):

        return jsonify({
            "error": "Latitude and longitude must be numbers"
        }), 400

    if not validate_coordinates(
        latitude,
        longitude
    ):
        return jsonify({
            "error": "Invalid latitude or longitude"
        }), 400

    existing = DumpingSite.query.filter_by(
        case_id=data["case_id"]
    ).first()

    if existing:
        return jsonify({
            "error": "A dumping site with this case_id already exists"
        }), 409

    now = datetime.utcnow()

    site = DumpingSite(
        case_id=data["case_id"],
        latitude=latitude,
        longitude=longitude,
        geometry=create_point(
            latitude,
            longitude
        ),
        area_m2=data.get("area_m2"),
        waste_probability=data.get(
            "waste_probability"
        ),
        confidence=data.get(
            "confidence"
        ),
        risk_score=data.get(
            "risk_score"
        ),
        risk_level=data.get(
            "risk_level"
        ),
        status=data["status"],
        ai_summary=data.get(
            "ai_summary"
        ),
        first_detected=data.get(
            "first_detected"
        ),
        last_detected=data.get(
            "last_detected"
        ),
        created_at=now,
        updated_at=now
    )

    db.session.add(site)
    db.session.commit()

    return jsonify(site.to_dict()), 201


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

@dumping_sites_bp.put("/<int:site_id>")
def update_dumping_site(site_id):

    site = db.session.get(
        DumpingSite,
        site_id
    )

    if site is None:
        return jsonify({
            "error": "Dumping site not found"
        }), 404

    data = request.get_json(silent=True) or {}

    if "latitude" in data:
        try:
            site.latitude = float(
                data["latitude"]
            )
        except (TypeError, ValueError):

            return jsonify({
                "error": "Latitude must be a number"
            }), 400

    if "longitude" in data:
        try:
            site.longitude = float(
                data["longitude"]
            )
        except (TypeError, ValueError):

            return jsonify({
                "error": "Longitude must be a number"
            }), 400

    if not validate_coordinates(
        site.latitude,
        site.longitude
    ):
        return jsonify({
            "error": "Invalid coordinates"
        }), 400

    if (
        "latitude" in data
        or "longitude" in data
    ):
        site.geometry = create_point(
            site.latitude,
            site.longitude
        )

    updateable_fields = [
        "case_id",
        "area_m2",
        "waste_probability",
        "confidence",
        "risk_score",
        "risk_level",
        "status",
        "ai_summary"
    ]

    for field in updateable_fields:

        if field in data:
            setattr(
                site,
                field,
                data[field]
            )

    if "first_detected" in data:
        site.first_detected = data[
            "first_detected"
        ]

    if "last_detected" in data:
        site.last_detected = data[
            "last_detected"
        ]

    site.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(site.to_dict()), 200


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

@dumping_sites_bp.delete("/<int:site_id>")
def delete_dumping_site(site_id):

    site = db.session.get(
        DumpingSite,
        site_id
    )

    if site is None:
        return jsonify({
            "error": "Dumping site not found"
        }), 404

    db.session.delete(site)
    db.session.commit()

    return jsonify({
        "message": "Dumping site deleted",
        "id": site_id
    }), 200


# ---------------------------------------------------------
# GEOJSON
# ---------------------------------------------------------

@dumping_sites_bp.get("/geojson")
def dumping_sites_geojson():

    sites = (
        DumpingSite.query
        .order_by(DumpingSite.created_at.desc())
        .all()
    )

    features = []

    for site in sites:

        features.append({
            "type": "Feature",

            "geometry": site.geometry_geojson(),

            "properties": {
                "id": site.id,
                "case_id": site.case_id,
                "area_m2": site.area_m2,
                "waste_probability": site.waste_probability,
                "confidence": site.confidence,
                "risk_score": site.risk_score,
                "risk_level": site.risk_level,
                "status": site.status,
                "ai_summary": site.ai_summary,
                "first_detected": (
                    site.first_detected.isoformat()
                    if site.first_detected
                    else None
                ),
                "last_detected": (
                    site.last_detected.isoformat()
                    if site.last_detected
                    else None
                )
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    }), 200


# ---------------------------------------------------------
# NEARBY SEARCH
# ---------------------------------------------------------

@dumping_sites_bp.get("/nearby")
def nearby_dumping_sites():

    try:
        latitude = float(
            request.args["latitude"]
        )

        longitude = float(
            request.args["longitude"]
        )

        radius_m = float(
            request.args.get(
                "radius",
                5000
            )
        )

    except (KeyError, TypeError, ValueError):

        return jsonify({
            "error": (
                "latitude, longitude and "
                "radius must be valid numbers"
            )
        }), 400

    if not validate_coordinates(
        latitude,
        longitude
    ):
        return jsonify({
            "error": "Invalid coordinates"
        }), 400

    if radius_m <= 0:
        return jsonify({
            "error": "radius must be greater than zero"
        }), 400

    reference_point = func.ST_SetSRID(
        func.ST_MakePoint(
            longitude,
            latitude
        ),
        4326
    )

    distance = func.ST_Distance(
        DumpingSite.geometry,
        reference_point,
        True
    )

    sites = (
        DumpingSite.query
        .filter(
            func.ST_DWithin(
                DumpingSite.geometry,
                reference_point,
                radius_m,
                True
            )
        )
        .order_by(distance)
        .all()
    )

    results = []

    for site in sites:

        item = site.to_dict()

        item["distance_m"] = round(
            float(
                db.session.query(
                    func.ST_Distance(
                        DumpingSite.geometry,
                        reference_point,
                        True
                    )
                )
                .filter(
                    DumpingSite.id == site.id
                )
                .scalar()
            ),
            2
        )

        results.append(item)

    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "radius_m": radius_m,
        "count": len(results),
        "data": results
    }), 200
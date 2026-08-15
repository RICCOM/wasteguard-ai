# import random
# from datetime import datetime

# from extensions import db
# from models.dumping_site import DumpingSite


# # Nairobi area used for the prototype simulation
# BASE_LATITUDE = -1.286389
# BASE_LONGITUDE = 36.817223


# def calculate_risk_score(waste_probability, confidence, area_m2):
#     """
#     Calculate a risk score between 0 and 100.
#     """

#     probability_score = waste_probability * 50
#     confidence_score = confidence * 30

#     # Larger dumping areas increase risk.
#     area_score = min(area_m2 / 10, 20)

#     score = probability_score + confidence_score + area_score

#     return min(round(score), 100)


# def get_risk_level(score):
#     if score >= 85:
#         return "CRITICAL"

#     if score >= 70:
#         return "HIGH"

#     if score >= 40:
#         return "MEDIUM"

#     return "LOW"


# def generate_case_id():
#     """
#     Generate the next WasteGuard case ID.
#     """

#     count = DumpingSite.query.count() + 1

#     return f"WG-KE-{count:04d}"


# def run_detection():
#     """
#     Simulate an AI illegal dumping detection.
#     """

#     # Generate a location near Nairobi.
#     latitude = BASE_LATITUDE + random.uniform(-0.03, 0.03)

#     longitude = BASE_LONGITUDE + random.uniform(-0.03, 0.03)

#     # Simulated AI model outputs.
#     waste_probability = round(random.uniform(0.55, 0.99), 2)

#     confidence = round(random.uniform(0.65, 0.99), 2)

#     area_m2 = round(random.uniform(20, 500), 2)

#     risk_score = calculate_risk_score(
#         waste_probability,
#         confidence,
#         area_m2,
#     )

#     risk_level = get_risk_level(risk_score)

#     site = DumpingSite(
#         case_id=generate_case_id(),
#         latitude=latitude,
#         longitude=longitude,
#         area_m2=area_m2,
#         waste_probability=waste_probability,
#         confidence=confidence,
#         risk_score=risk_score,
#         risk_level=risk_level,
#         status="detected",
#         ai_summary=(
#             f"AI detected a potential illegal dumping site "
#             f"with {waste_probability * 100:.0f}% waste probability "
#             f"and {confidence * 100:.0f}% confidence."
#         ),
#         first_detected=datetime.utcnow(),
#         last_detected=datetime.utcnow(),
#     )

#     db.session.add(site)
#     db.session.commit()

#     return site
import random
from datetime import datetime

from geoalchemy2.elements import WKTElement

from extensions import db
from models.dumping_site import DumpingSite


# Prototype area: Nairobi and surrounding locations
BASE_LATITUDE = -1.286389
BASE_LONGITUDE = 36.817223


def calculate_risk_score(waste_probability, confidence, area_m2):
    """
    Calculate a risk score between 0 and 100.
    """

    probability_score = waste_probability * 50
    confidence_score = confidence * 30

    # Larger dumping areas increase risk
    area_score = min(area_m2 / 10, 20)

    score = (
        probability_score
        + confidence_score
        + area_score
    )

    return min(round(score), 100)


def get_risk_level(score):
    """
    Convert a numerical risk score into a risk category.
    """

    if score >= 85:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def generate_case_id():
    """
    Generate the next WasteGuard Kenya case ID.
    """

    count = DumpingSite.query.count() + 1

    return f"WG-KE-{count:04d}"


def run_detection():
    """
    Simulate an AI-powered illegal dumping detection.
    """

    # Generate a random location near Nairobi
    latitude = BASE_LATITUDE + random.uniform(-0.03, 0.03)

    longitude = BASE_LONGITUDE + random.uniform(-0.03, 0.03)

    # Simulated AI detection outputs
    waste_probability = round(
        random.uniform(0.55, 0.99),
        2
    )

    confidence = round(
        random.uniform(0.65, 0.99),
        2
    )

    area_m2 = round(
        random.uniform(20, 500),
        2
    )

    # Calculate risk
    risk_score = calculate_risk_score(
        waste_probability,
        confidence,
        area_m2,
    )

    risk_level = get_risk_level(risk_score)

    # PostGIS requires POINT(longitude latitude)
    geometry = WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )

    site = DumpingSite(
        case_id=generate_case_id(),
        latitude=latitude,
        longitude=longitude,
        geometry=geometry,
        area_m2=area_m2,
        waste_probability=waste_probability,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_level,
        status="detected",
        ai_summary=(
            f"AI detected a potential illegal dumping site "
            f"with {waste_probability * 100:.0f}% waste probability "
            f"and {confidence * 100:.0f}% confidence."
        ),
        first_detected=datetime.utcnow(),
        last_detected=datetime.utcnow(),
    )

    db.session.add(site)
    db.session.commit()

    return site
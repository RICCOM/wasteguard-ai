import ee

from services.satellite_service import (
    initialize_earth_engine,
    get_before_after_images,
)


def calculate_change_image(before, after):
    """
    Calculate spectral change between the baseline
    and recent Sentinel-2 composites.

    We use visible and near-infrared bands.
    """

    bands = ["B2", "B3", "B4", "B8"]

    before_image = before.select(bands)
    after_image = after.select(bands)

    difference = after_image.subtract(before_image)

    change = difference.abs().reduce(
        ee.Reducer.mean()
    )

    return change.rename("change_score")


def detect_changed_areas(
    threshold=0.08,
    min_area_m2=100,
):
    """
    Detect candidate areas with significant
    spectral change.

    Returns an Earth Engine FeatureCollection.
    """

    initialize_earth_engine()

    imagery = get_before_after_images()

    before = imagery["before"]["image"]
    after = imagery["after"]["image"]
    region = imagery["region"]

    change_image = calculate_change_image(
        before,
        after,
    )

    changed_pixels = change_image.gt(threshold)

    vectors = (
        changed_pixels
        .selfMask()
        .reduceToVectors(
            geometry=region,
            scale=10,
            geometryType="polygon",
            eightConnected=True,
            labelProperty="change",
            reducer=ee.Reducer.countEvery(),
            maxPixels=1e9,
        )
    )

    # def add_area(feature):
    #     area = feature.geometry().area()

    #     return feature.set({
    #         "area_m2": area
    #     })
    def add_area(feature):
       """
       Calculate the area of each detected polygon.
       """

       area = feature.geometry().area(
        maxError=ee.ErrorMargin(1)
       )

       return feature.set(
        "area_m2",
        area
    )

    candidates = (
        vectors
        .map(add_area)
        .filter(
            ee.Filter.gte(
                "area_m2",
                min_area_m2,
            )
        )
    )

    return {
        "candidates": candidates,
        "change_image": change_image,
        "before": before,
        "after": after,
        "region": region,
    }


def get_detection_summary(
    threshold=0.08,
    min_area_m2=100,
):
    """
    Run change detection and return a summary.
    """

    result = detect_changed_areas(
        threshold=threshold,
        min_area_m2=min_area_m2,
    )

    candidate_count = (
        result["candidates"]
        .size()
        .getInfo()
    )

    return {
        "candidate_count": candidate_count,
        "threshold": threshold,
        "min_area_m2": min_area_m2,
    }
def extract_top_candidates(
    threshold=0.25,
    min_area_m2=500,
    limit=20,
):
    """
    Extract and rank the strongest satellite-derived
    change candidates.

    These are suspicious change locations, not yet
    confirmed illegal dumping sites.
    """

    initialize_earth_engine()

    result = detect_changed_areas(
        threshold=threshold,
        min_area_m2=min_area_m2,
    )

    candidates = result["candidates"]
    change_image = result["change_image"]

    def enrich_candidate(feature):
        geometry = feature.geometry()

        area = geometry.area(
            maxError=ee.ErrorMargin(1)
        )

        centroid = geometry.centroid(
            maxError=ee.ErrorMargin(1)
        )

        change_score = change_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=10,
            maxPixels=1e8,
        ).get("change_score")

        coordinates = centroid.coordinates()

        return feature.set({
            "area_m2": area,
            "longitude": coordinates.get(0),
            "latitude": coordinates.get(1),
            "change_score": change_score,
        })

    enriched = candidates.map(enrich_candidate)

    ranked = (
        enriched
        .sort("change_score", False)
        .limit(limit)
    )

    features = ranked.getInfo()["features"]

    results = []

    for feature in features:
        properties = feature["properties"]

        results.append({
            "longitude": properties.get("longitude"),
            "latitude": properties.get("latitude"),
            "area_m2": properties.get("area_m2"),
            "change_score": properties.get("change_score"),
        })

    return results
def extract_ranked_candidates(
    threshold=0.25,
    min_area_m2=500,
    max_area_m2=10000,
    min_change_score=0.30,
    limit=10,
):
    """
    Extract localized satellite-change candidates and
    rank them by change intensity and area.

    These are suspicious candidates, not confirmed
    illegal dumping sites.
    """

    candidates = extract_top_candidates(
        threshold=threshold,
        min_area_m2=min_area_m2,
        limit=100,
    )

    filtered = [
        candidate
        for candidate in candidates
        if (
            min_area_m2
            <= candidate["area_m2"]
            <= max_area_m2
            and candidate["change_score"] >= min_change_score
        )
    ]

    def calculate_candidate_score(candidate):
        """
        Score candidates using:

        - spectral change intensity
        - localized area preference
        """

        normalized_change = min(
            candidate["change_score"] / 0.75,
            1.0,
        )

        normalized_area = min(
            candidate["area_m2"] / max_area_m2,
            1.0,
        )

        # Prefer meaningful but localized areas.
        area_score = 1 - abs(
            normalized_area - 0.3
        )

        score = (
            normalized_change * 0.7
            + area_score * 0.3
        )

        return round(score, 4)

    for candidate in filtered:
        candidate["candidate_score"] = (
            calculate_candidate_score(candidate)
        )

    ranked = sorted(
        filtered,
        key=lambda candidate: candidate["candidate_score"],
        reverse=True,
    )

    return ranked[:limit]
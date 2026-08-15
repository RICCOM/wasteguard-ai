from flask import Blueprint, jsonify

from services.detection_service import run_detection


detections_bp = Blueprint(
    "detections",
    __name__,
    url_prefix="/api/detections"
)


@detections_bp.route("/run", methods=["POST"])
def run_ai_detection():
    try:
        site = run_detection()

        return jsonify({
            "success": True,
            "message": "AI detection completed successfully",
            "data": site.to_dict()
        }), 201

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "AI detection failed",
            "error": str(error)
        }), 500
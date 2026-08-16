import { useEffect, useState } from "react";
import L from "leaflet";
import {
  GeoJSON,
  MapContainer,
  TileLayer,
} from "react-leaflet";

import { getDumpingSitesGeoJSON } from "../services/api";

function getRiskColor(riskLevel) {
  switch (riskLevel) {
    case "CRITICAL":
      return "#dc2626";
    case "HIGH":
      return "#f97316";
    case "MEDIUM":
      return "#eab308";
    case "LOW":
      return "#22c55e";
    default:
      return "#64748b";
  }
}

export default function DumpingMap() {
  const [geojson, setGeojson] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDumpingSitesGeoJSON()
      .then((data) => {
        setGeojson(data);
      })
      .catch((err) => {
        console.error("Map error:", err);
        setError(err.message);
      });
  }, []);

  const pointToLayer = (feature, latlng) => {
    const riskLevel = feature.properties?.risk_level;
    const fillColor = getRiskColor(riskLevel);

    return L.circleMarker(latlng, {
      radius: 11,
      fillColor,
      color: "#ffffff",
      weight: 3,
      opacity: 1,
      fillOpacity: 0.9,
    });
  };

  const onEachFeature = (feature, layer) => {
    const site = feature.properties;

    layer.bindPopup(`
      <div class="popup-content">
        <div class="popup-header">
          <strong>${site.case_id}</strong>
          <span>${site.risk_level}</span>
        </div>

        <div class="popup-grid">
          <p>
            <strong>Risk Score</strong>
            ${site.risk_score}
          </p>

          <p>
            <strong>Waste Probability</strong>
            ${Math.round(site.waste_probability * 100)}%
          </p>

          <p>
            <strong>AI Confidence</strong>
            ${Math.round(site.confidence * 100)}%
          </p>

          <p>
            <strong>Estimated Area</strong>
            ${Number(site.area_m2 || 0).toLocaleString()} m²
          </p>
        </div>

        <p class="popup-status">
          Status: ${site.status}
        </p>

        ${
          site.ai_summary
            ? `<p class="popup-summary">${site.ai_summary}</p>`
            : ""
        }
      </div>
    `);
  };

  if (error) {
    return (
      <div className="map-error">
        <div>
          <strong>Unable to load map data</strong>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="map-wrapper">
      <MapContainer
        center={[-1.286389, 36.817223]}
        zoom={12}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        {geojson && (
          <GeoJSON
            data={geojson}
            pointToLayer={pointToLayer}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>

      <div className="map-legend">
        <h4>Risk Level</h4>

        <div>
          <span className="legend-dot critical" />
          Critical
        </div>

        <div>
          <span className="legend-dot high" />
          High
        </div>

        <div>
          <span className="legend-dot medium" />
          Medium
        </div>

        <div>
          <span className="legend-dot low" />
          Low
        </div>
      </div>
    </div>
  );
}
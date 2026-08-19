import { useEffect, useState } from "react";
import L from "leaflet";

import {
  MapContainer,
  TileLayer,
  GeoJSON,
  useMap,
} from "react-leaflet";

import { getDumpingSitesGeoJSON } from "../services/api";

function MapController({ selectedSite }) {
  const map = useMap();

  useEffect(() => {
    if (selectedSite?.latitude && selectedSite?.longitude) {
      map.flyTo(
        [
          selectedSite.latitude,
          selectedSite.longitude,
        ],
        15,
        {
          duration: 1,
        }
      );
    }
  }, [selectedSite, map]);

  return null;
}

export default function DumpingMap({
  selectedSite,
  setSelectedSite,
}) {
  const [geojson, setGeojson] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDumpingSitesGeoJSON()
      .then((data) => {
        console.log(
          "GeoJSON loaded:",
          data
        );

        setGeojson(data);
      })
      .catch((err) => {
        console.error(
          "Map error:",
          err
        );

        setError(err.message);
      });
  }, []);

  function getMarkerColor(risk) {
    if (risk === "CRITICAL") {
      return "#dc2626";
    }

    if (risk === "HIGH") {
      return "#f97316";
    }

    if (risk === "MEDIUM") {
      return "#eab308";
    }

    return "#22c55e";
  }

  const pointToLayer = (
    feature,
    latlng
  ) => {
    const risk =
      feature.properties?.risk_level;

    return L.circleMarker(latlng, {
      radius: 11,
      fillColor:
        getMarkerColor(risk),
      color: "#ffffff",
      weight: 3,
      opacity: 1,
      fillOpacity: 0.95,
    });
  };

  const onEachFeature = (
    feature,
    layer
  ) => {
    const site = feature.properties;

    layer.on({
      click: () => {
        const coordinates =
          feature.geometry.coordinates;

        setSelectedSite({
          ...site,
          longitude: coordinates[0],
          latitude: coordinates[1],
        });
      },
    });

    const detectedDate =
      site.first_detected
        ? new Date(
            site.first_detected
          ).toLocaleString("en-KE")
        : "Not available";

    layer.bindPopup(`
      <div style="min-width:220px;">
        <h3 style="margin-top:0;">
          ${site.case_id}
        </h3>

        <p>
          <strong>Risk:</strong>
          ${site.risk_level}
        </p>

        <p>
          <strong>Score:</strong>
          ${site.risk_score}
        </p>

        <p>
          <strong>Waste Probability:</strong>
          ${Math.round(
            site.waste_probability * 100
          )}%
        </p>

        <p>
          <strong>Confidence:</strong>
          ${Math.round(
            site.confidence * 100
          )}%
        </p>

        <p>
          <strong>Area:</strong>
          ${site.area_m2} m²
        </p>

        <p>
          <strong>Detected:</strong>
          ${detectedDate}
        </p>
      </div>
    `);
  };

  if (error) {
    return (
      <div className="map-error">
        Map Error: {error}
      </div>
    );
  }

  return (
    <MapContainer
      center={[-1.286389, 36.817223]}
      zoom={12}
      style={{
        height: "100%",
        width: "100%",
      }}
    >

      <MapController
        selectedSite={selectedSite}
      />

      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      {geojson && (
        <GeoJSON
          key={JSON.stringify(
            geojson
          )}
          data={geojson}
          pointToLayer={pointToLayer}
          onEachFeature={onEachFeature}
        />
      )}

    </MapContainer>
  );
}
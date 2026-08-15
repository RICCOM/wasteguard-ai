// import { useEffect, useState } from "react";
// import {
//   MapContainer,
//   TileLayer,
//   GeoJSON,
//   Popup,
// } from "react-leaflet";
// import L from "leaflet";

// import { getDumpingSitesGeoJSON } from "../services/api";

// export default function DumpingMap() {
//   const [geojson, setGeojson] = useState(null);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     getDumpingSitesGeoJSON()
//       .then((data) => {
//         setGeojson(data);
//       })
//       .catch((err) => {
//         console.error(err);
//         setError(err.message);
//       });
//   }, []);

//   if (error) {
//     return (
//       <div className="flex h-full items-center justify-center text-red-600">
//         Failed to load dumping sites: {error}
//       </div>
//     );
//   }

//   return (
//     <MapContainer
//       center={[-1.286389, 36.817223]}
//       zoom={12}
//       className="h-full w-full"
//     >
//       <TileLayer
//         attribution="&copy; OpenStreetMap contributors"
//         url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//       />

//       {geojson && (
//         <GeoJSON
//           data={geojson}
//           pointToLayer={(feature, latlng) => {
//             return L.circleMarker(latlng, {
//               radius: 10,
//               fillOpacity: 0.85,
//               weight: 2,
//             });
//           }}
//           onEachFeature={(feature, layer) => {
//             const site = feature.properties;

//             layer.bindPopup(`
//               <div>
//                 <strong>${site.case_id}</strong>
//                 <br />
//                 Risk: ${site.risk_level}
//                 <br />
//                 Risk Score: ${site.risk_score}
//                 <br />
//                 Waste Probability: ${Math.round(
//                   site.waste_probability * 100
//                 )}%
//                 <br />
//                 AI Confidence: ${Math.round(
//                   site.confidence * 100
//                 )}%
//                 <br />
//                 Area: ${site.area_m2} m²
//               </div>
//             `);
//           }}
//         />
//       )}
//     </MapContainer>
//   );
// }
import { useEffect, useState } from "react";
import L from "leaflet";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
} from "react-leaflet";

import { getDumpingSitesGeoJSON } from "../services/api";

export default function DumpingMap() {
  const [geojson, setGeojson] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDumpingSitesGeoJSON()
      .then((data) => {
        console.log("GeoJSON loaded:", data);
        setGeojson(data);
      })
      .catch((err) => {
        console.error("Map error:", err);
        setError(err.message);
      });
  }, []);

  const pointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 12,
      fillColor: "#ef4444",
      color: "#ffffff",
      weight: 3,
      opacity: 1,
      fillOpacity: 0.9,
    });
  };

  const onEachFeature = (feature, layer) => {
    const site = feature.properties;

    layer.bindPopup(`
      <div style="min-width: 200px;">
        <h3>${site.case_id}</h3>
        <p><strong>Risk:</strong> ${site.risk_level}</p>
        <p><strong>Risk Score:</strong> ${site.risk_score}</p>
        <p>
          <strong>Waste Probability:</strong>
          ${Math.round(site.waste_probability * 100)}%
        </p>
        <p>
          <strong>AI Confidence:</strong>
          ${Math.round(site.confidence * 100)}%
        </p>
        <p>
          <strong>Area:</strong> ${site.area_m2} m²
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
      zoom={13}
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
  );
}
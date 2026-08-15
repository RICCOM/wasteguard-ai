import { useEffect, useState } from "react";
import DumpingMap from "./components/DumpingMap";
import { getDumpingSites } from "./services/api";

function App() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDumpingSites()
      .then((result) => {
        setSites(result.data);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const highRisk = sites.filter(
    (site) => site.risk_level === "HIGH"
  ).length;

  const totalArea = sites.reduce(
    (total, site) => total + (site.area_m2 || 0),
    0
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>WasteGuard AI</h1>
          <p>
            Illegal Dumping Monitoring & Intelligence Platform
          </p>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="error-message">
            API Error: {error}
          </div>
        )}

        <div className="stats-grid">
          <div className="stat-card">
            <p className="stat-label">Total Cases</p>
            <p className="stat-value">
              {loading ? "..." : sites.length}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">High Risk Cases</p>
            <p className="stat-value high-risk">
              {loading ? "..." : highRisk}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">Detected Area</p>
            <p className="stat-value">
              {loading
                ? "..."
                : `${totalArea.toFixed(1)} m²`}
            </p>
          </div>
        </div>

        <section className="map-section">
          <div className="map-header">
            <h2>Dumping Site Monitoring Map</h2>
            <p>
              AI-detected potential illegal dumping locations
            </p>
          </div>

          <div className="map-container">
            <DumpingMap />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
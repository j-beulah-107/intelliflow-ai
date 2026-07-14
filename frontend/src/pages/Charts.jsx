import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

function Charts() {
  const [searchParams] = useSearchParams();

  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const generateCharts = async () => {
      const fileId =
        searchParams.get("fileId");

      if (!fileId) return;

      setLoading(true);

      try {
        const token =
          localStorage.getItem(
            "access_token"
          );

        const response =
          await axios.post(
            `http://127.0.0.1:8000/charts/${fileId}`,
            {},
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

        setCharts(
          response.data.charts || []
        );
      } catch (error) {
        setMessage(
          error.response?.data?.detail ||
            "Unable to generate charts."
        );
      }

      setLoading(false);
    };

    generateCharts();
  }, []);

  return (
    <main className="dashboard-page">
      <h1>Generated Charts</h1>

      {loading && (
        <p>Generating charts...</p>
      )}

      {message && <p>{message}</p>}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(300px,1fr))",
          gap: "20px",
        }}
      >
        {charts.map((chart) => (
          <div key={chart.stored_name}>
            <h3>{chart.column}</h3>

            <img
              src={`http://127.0.0.1:8000/charts/${chart.stored_name}`}
              alt={chart.column}
              style={{
                width: "100%",
                borderRadius: "10px",
              }}
            />
          </div>
        ))}
      </div>
    </main>
  );
}

export default Charts;
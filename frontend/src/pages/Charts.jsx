import { useEffect, useState } from "react";
import {
  Link,
  useSearchParams,
} from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";

function Charts() {
  const [searchParams] =
    useSearchParams();

  const [charts, setCharts] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [message, setMessage] =
    useState("");

  useEffect(() => {
    const generateCharts =
      async () => {
        const fileId =
          searchParams.get(
            "fileId"
          );

        if (!fileId) {
          setMessage(
            "Please upload or select a CSV file to generate charts."
          );
          return;
        }

        setLoading(true);
        setMessage("");

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
                  Authorization:
                    `Bearer ${token}`,
                },
              }
            );

          setCharts(
            response.data
              .charts || []
          );
        } catch (error) {
          setMessage(
            error.response?.data
              ?.detail ||
              "Unable to generate charts."
          );
        } finally {
          setLoading(false);
        }
      };

    generateCharts();
  }, [searchParams]);

  return (
    <>
      <Navbar />

      <main className="dashboard-page">
        <header className="page-header">
          <div>
            <h1>
              Generated Charts
            </h1>

            <p>
              View visualisations
              created from your
              CSV dataset.
            </p>
          </div>

          <Link
            className="secondary-button"
            to="/dashboard"
          >
            Back to Dashboard
          </Link>
        </header>

        {loading && (
          <div className="content-card">
            <p>
              Generating charts...
            </p>
          </div>
        )}

        {message && (
          <div className="content-card">
            <p>{message}</p>
          </div>
        )}

        {!loading &&
          charts.length > 0 && (
            <section className="chart-grid">
              {charts.map(
                (chart) => (
                  <article
                    className="chart-card"
                    key={
                      chart.stored_name
                    }
                  >
                    <h2>
                      {
                        chart.column
                      }
                    </h2>

                    <p>
                      Data
                      visualisation
                    </p>

                    <img
                      src={`http://127.0.0.1:8000/charts/${chart.stored_name}`}
                      alt={`Chart for ${chart.column}`}
                    />
                  </article>
                )
              )}
            </section>
          )}
      </main>
    </>
  );
}

export default Charts;
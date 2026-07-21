import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";

function Files() {
  const [files, setFiles] = useState([]);
  const [message, setMessage] =
    useState("");

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const token =
        localStorage.getItem(
          "access_token"
        );

      const response =
        await axios.get(
          "http://127.0.0.1:8000/files",
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      setFiles(response.data);
    } catch (error) {
      console.log(error);
      setMessage(
        "Unable to load files."
      );
    }
  };

  const deleteFile =
    async (fileId) => {
      const confirmed =
        window.confirm(
          "Are you sure you want to delete this file?"
        );

      if (!confirmed) {
        return;
      }

      try {
        const token =
          localStorage.getItem(
            "access_token"
          );

        await axios.delete(
          `http://127.0.0.1:8000/files/${fileId}`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        setMessage(
          "File deleted successfully."
        );

        loadFiles();
      } catch (error) {
        console.log(error);

        setMessage(
          error.response?.data
            ?.detail ||
            "Unable to delete file."
        );
      }
    };

  return (
    <>
      <Navbar />

      <main className="dashboard-page">
        <header className="page-header">
          <div>
            <h1>
              Uploaded Files
            </h1>

            <p>
              View and manage
              your uploaded
              documents.
            </p>
          </div>

          <Link
            className="secondary-button"
            to="/dashboard"
          >
            Back to Dashboard
          </Link>
        </header>

        {message && (
          <p>{message}</p>
        )}

        {files.length === 0 ? (
          <div className="content-card">
            <p>
              No uploaded files
              found.
            </p>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gap: "20px",
            }}
          >
            {files.map(
              (file) => (
                <div
                  key={
                    file.id
                  }
                  className="content-card"
                >
                  <h2>
                    {
                      file.original_name
                    }
                  </h2>

                  <p>
                    <strong>
                      Type:
                    </strong>{" "}
                    {
                      file.file_type
                    }
                  </p>

                  <p>
                    <strong>
                      File ID:
                    </strong>{" "}
                    {
                      file.id
                    }
                  </p>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      deleteFile(
                        file.id
                      )
                    }
                    style={{
                      marginTop:
                        "15px",
                    }}
                  >
                    Delete File
                  </button>
                </div>
              )
            )}
          </div>
        )}
      </main>
    </>
  );
}

export default Files;
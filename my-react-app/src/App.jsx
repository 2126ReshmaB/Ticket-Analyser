import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [itoTickets, setItoTickets] = useState([]);
  const [nonItoTickets, setNonItoTickets] = useState([]);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
  };

  useEffect(() => {
    fetch("http://localhost:5000/get-ito-tickets")
      .then((res) => res.json())
      .then((json) => {
        setItoTickets(json.ito || []);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  useEffect(() => {
    fetch("http://localhost:5000/get-non-ito-tickets")
      .then((res) => res.json())
      .then((json) => {
        setNonItoTickets(json.non_ito || []);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("Upload successful!");
      console.log(res.data);
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Upload failed.");
    }
  };

  const renderTable = (data, title) => (
    <div style={{ marginBottom: "40px" }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>{title}</h2>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
        }}
      >
        <thead style={{ backgroundColor: "#f0f0f0" }}>
          <tr>
            <th style={thStyle}>Category</th>
            <th style={thStyle}>Description</th>
            <th style={thStyle}>Short Description</th>
            <th style={thStyle}>Predicted Label</th>
          </tr>
        </thead>
        <tbody>
          {data.map((ticket, index) => (
            <tr key={index} style={{ textAlign: "center" }}>
              <td style={tdStyle}>{ticket.Category}</td>
              <td style={tdStyle}>{ticket.Description}</td>
              <td style={tdStyle}>{ticket.Short_Description}</td>
              <td style={tdStyle}>{ticket.predicted_label}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ textAlign: "center", marginBottom: "30px" }}>
        Ticket Analyzer
      </h1>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginBottom: "50px",
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            padding: "30px",
            border: "1px solid #ddd",
            borderRadius: "10px",
            backgroundColor: "#f9f9f9",
            width: "400px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          }}
        >
          <input
            type="file"
            onChange={handleChange}
            style={{
              padding: "12px",
              fontSize: "16px",
              borderRadius: "6px",
              border: "1px solid #ccc",
              cursor: "pointer",
            }}
          />
          <button
            type="submit"
            style={{
              padding: "12px",
              backgroundColor: "#007BFF",
              color: "#fff",
              fontSize: "16px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Upload
          </button>
        </form>
      </div>

      {renderTable(itoTickets, "ITO Tickets")}
      {renderTable(nonItoTickets, "Non-ITO Tickets")}
    </div>
  );
}

const thStyle = {
  padding: "12px",
  border: "1px solid #ccc",
  backgroundColor: "#eaeaea",
};

const tdStyle = {
  padding: "12px",
  border: "1px solid #ddd",
};

export default App;

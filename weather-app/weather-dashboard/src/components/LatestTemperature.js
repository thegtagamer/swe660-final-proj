import React, { useEffect, useState } from "react";
import socket from "../services/socketService";

const LatestTemperature = () => {
  const [temperature, setTemperature] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Connect to the WebSocket
    socket.on("connect", () => {
      console.log("Connected to WebSocket server");

      // Request the latest temperature
      socket.emit("latest_temperature");
    });

    // Listen for the latest temperature updates
    socket.on("latest_temperature_response", (data) => {
      console.log("latest");
      setTemperature(data);
    });

    // Handle WebSocket errors
    socket.on("connect_error", (err) => {
      console.error("WebSocket connection error:", err);
      setError("Failed to connect to the server.");
    });

    // Cleanup on unmount
    return () => {
      socket.off("latest_temperature_response");
      socket.off("connect_error");
    };
  }, []);

  return (
    <div style={{ padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h2>Current Temperature</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {temperature ? (
        <div>
          <p>
            <strong>Temperature:</strong> {temperature.temperature}°C
          </p>
          <p>
            <strong>Timestamp:</strong> {new Date(temperature.timestamp).toLocaleString()}
          </p>
        </div>
      ) : (
        <p>Loading Current temperature...</p>
      )}
    </div>
  );
};

export default LatestTemperature;

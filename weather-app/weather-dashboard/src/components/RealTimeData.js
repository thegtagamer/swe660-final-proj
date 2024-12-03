import React from "react";
import useSocket from "../hooks/useSocket";

const RealTimeData = () => {
  const realTimeData = useSocket("http://localhost:9080");

  return (
    <div className="card bg-info text-white mt-4">
      <div className="card-body">
        <h5>Real-Time Data</h5>
        {realTimeData ? (
          <>
            <p>Temperature: {realTimeData.temperature_dht}°C</p>
            <p>Humidity: {realTimeData.humidity}%</p>
            <p>Timestamp: {new Date(realTimeData.timestamp * 1000).toLocaleString()}</p>
          </>
        ) : (
          <p>Waiting for real-time updates...</p>
        )}
      </div>
    </div>
  );
};

export default RealTimeData;

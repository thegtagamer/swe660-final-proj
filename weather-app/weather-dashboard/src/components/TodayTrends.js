import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import io from "socket.io-client";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TodayTrends = () => {
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Establish WebSocket connection
    const socket = io("http://localhost:9080");

    // Request today's trends
    socket.emit("today_trends");

    // Listen for the response
    socket.on("today_trends_response", (data) => {
      if (data.error) {
        setError(data.error);
      } else if (data.trends) {
        setTrends(data.trends);
      }
    });

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  // Prepare data for Chart.js
  const chartData = {
    labels: trends.map((entry) =>
      new Date(entry.timestamp).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      })
    ),
    datasets: [
      {
        label: "Temperature (°C)",
        data: trends.map((entry) => entry.temperature),
        borderColor: "rgba(75, 192, 192, 1)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        fill: true,
        tension: 0.4,
      },
      {
        label: "Humidity (%)",
        data: trends.map((entry) => entry.humidity),
        borderColor: "rgba(255, 99, 132, 1)",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Time",
        },
      },
      y: {
        title: {
          display: true,
          text: "Temperature (°C) and Humidity (%)",
        },
      },
    },
  };

  return (
    <div>
      <h2 style={{ textAlign: "center" }}>Today's Temperature and Humidity Trends</h2>
      {error ? (
        <p>Error: {error}</p>
      ) : trends.length === 0 ? (
        <p>Loading trends...</p>
      ) : (
        <div className="temp-graph">
          <Line key={JSON.stringify(chartData)} data={chartData} options={options} />
        </div>
      )}
    </div>
  );
};

export default TodayTrends;

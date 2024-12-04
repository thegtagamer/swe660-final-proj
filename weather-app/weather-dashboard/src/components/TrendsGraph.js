import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import axios from "axios";

const TrendsGraph = ({ apiUrl, title }) => {
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const response = await axios.get(apiUrl);
        setTrends(response.data);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchTrends();
  }, [apiUrl]);

// Determine label type dynamically
const getLabelKey = (trends) => {
  if (trends.length > 0) {
    if (trends[0].day) return "day"; // For daily data
    if (trends[0].week) return "week"; // For weekly data
    if (trends[0].month) return "month"; // For monthly data
  }
  return "timestamp"; // Default fallback (though unlikely for trends)
};

const labelKey = getLabelKey(trends);

const chartData = {
  labels: trends.map((entry) => entry[labelKey]), // Dynamically select label type
  datasets: [
    {
      label: "Avg Temperature (°C)",
      data: trends.map((entry) => entry.avg_temperature),
      borderColor: "rgba(75, 192, 192, 1)",
      backgroundColor: "rgba(75, 192, 192, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y",
    },
    {
      label: "Min Temperature (°C)",
      data: trends.map((entry) => entry.min_temperature),
      borderColor: "rgba(54, 162, 235, 1)",
      backgroundColor: "rgba(54, 162, 235, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y",
    },
    {
      label: "Max Temperature (°C)",
      data: trends.map((entry) => entry.max_temperature),
      borderColor: "rgba(255, 99, 132, 1)",
      backgroundColor: "rgba(255, 99, 132, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y",
    },
    {
      label: "Avg Humidity (%)",
      data: trends.map((entry) => entry.avg_humidity),
      borderColor: "rgba(153, 102, 255, 1)",
      backgroundColor: "rgba(153, 102, 255, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y1", // Secondary Y-axis for humidity
    },
    {
      label: "Min Humidity (%)",
      data: trends.map((entry) => entry.min_humidity),
      borderColor: "rgba(255, 159, 64, 1)",
      backgroundColor: "rgba(255, 159, 64, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y1", // Secondary Y-axis for humidity
    },
    {
      label: "Max Humidity (%)",
      data: trends.map((entry) => entry.max_humidity),
      borderColor: "rgba(201, 203, 207, 1)",
      backgroundColor: "rgba(201, 203, 207, 0.2)",
      fill: true,
      tension: 0.4,
      yAxisID: "y1", // Secondary Y-axis for humidity
    },
  ]
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
        text: "Day",
      },
    },
    y: {
      title: {
        display: true,
        text: "Temperature (°C)",
      },
      position: "left",
    },
    y1: {
      title: {
        display: true,
        text: "Humidity (%)",
      },
      position: "right",
      grid: {
        drawOnChartArea: false, // Prevent gridlines overlapping with the left y-axis
      },
    },
  },
};




  return (
    <div>
      {error ? (
        <p>Error: {error}</p>
      ) : trends.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <div className="temp-graph">
          <Line data={chartData} options={options} />
        </div>
      )}
    </div>
  );
};

export default TrendsGraph;

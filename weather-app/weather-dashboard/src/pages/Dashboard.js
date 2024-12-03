import React, { useEffect, useState } from "react";
import socket from "../services/socketService";
import Header from "../components/Header";
import Footer from "../components/Footer";
// import StatCard from "../components/Card/StatCard";
// import TodayChart from "../components/Charts/TodayChart";
// import WeeklyChart from "../components/Charts/WeeklyChart";
// import RealTimeData from "../components/RealTimeData";
import LatestTemperature from "../components/LatestTemperature";
import TodayTrends from "../components/TodayTrends";
import TrendsGraph from "../components/TrendsGraph";
import { FaTree, FaHome, FaCloud } from "react-icons/fa";
import Card from "../components/Card/Card";
import "./Dashboard.css"

// import api from "../services/api";

const Dashboard = () => {
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


  const cardsData = [
    {
      icon: <FaHome size={40} color="#fff" />,
      temperature: temperature && temperature.temperature || 'Loading',
      title: "Current Temperature",
      bgColor: "#007bff", // Blue
    },
    {
      icon: <FaTree size={40} color="#fff" />,
      humidity: temperature && temperature.humidity || 'Loading',
      title: "Current Humidity",
      // subtitle: "",
      bgColor: "#28a745", // Green
    }
    // {
    //   icon: <FaCloud size={40} color="#fff" />,
    //   temperature: null,
    //   humidity: null,
    //   title: "Clear throughout the day",
    //   subtitle: "Details on Forecast.io",
    //   // bgColor: "#ffc107", // Yellow
    // },
  ];

  return (
    <div>
      <Header />

      <div className="cardSection">
      <div className="cards-container">
        {cardsData.map((card, index) => (
          <div
            key={index}
            style={{ backgroundColor: card.bgColor, color: "#fff" }}
            className="card-wrapper"
          >
            <Card
              icon={card.icon}
              temperature={card.temperature}
              humidity={card.humidity}
              title={card.title}
              subtitle={card.subtitle}
            />
          </div>
        ))}
      </div>
    </div>


      {/* <LatestTemperature /> */}
      <TodayTrends />

      <div>
      <h1>Weather Trends Dashboard</h1>
      <TrendsGraph apiUrl="http://localhost:9080/trends/weekly" title="Weekly Trends" />
      <TrendsGraph apiUrl="http://localhost:9080/trends/monthly" title="Monthly Trends" />
      <TrendsGraph apiUrl="http://localhost:9080/trends/yearly" title="Yearly Trends" />
      <TrendsGraph
        apiUrl="http://localhost:9080/trends/custom?start_date=2024-12-01T00:00:00&end_date=2024-12-07T23:59:59"
        title="Custom Date Range Trends"
      />
    </div>


      <Footer />
    </div>
  );
};

export default Dashboard;

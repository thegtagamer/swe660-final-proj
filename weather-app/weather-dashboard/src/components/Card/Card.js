import React from "react";
import "./Card.css"; // Import custom CSS for card styling

const Card = ({ icon, temperature, humidity, title, subtitle }) => {
  return (
    <div className="card">
      {icon}       
      <h4>{title}</h4> 
      {temperature ? (<h2>{temperature}°</h2>): (<h2>{humidity}</h2> )}
      <p>{subtitle}</p>
      </div>
  );
};

export default Card;
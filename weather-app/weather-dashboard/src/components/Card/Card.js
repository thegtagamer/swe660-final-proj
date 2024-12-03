import React from "react";
import "./Card.css"; // Import custom CSS for card styling

const Card = ({ icon, temperature, humidity, title, subtitle }) => {
  return (
    <div className="card">
      <div className="card-header">
        {icon}
        
        {temperature ?
        
      (<h2>{temperature}°</h2>): (<h2>{humidity}</h2>
      )}
      </div>
      <h4>{title}</h4>
      {/* <p>{subtitle}</p> */}
  
      </div>
   

  );
};

export default Card;

import React, { useEffect, useState } from "react";
import axios from "axios";
import './foodlist.css';

function Foodlist() {
    const[fooditem, setfooditem] = useState([]);
    
    useEffect(() => {
  axios
    .get("http://127.0.0.1:8005/api/foodlist/")
    .then((response) => {
      console.log("API Response:", response.data); // 👀 check what you get
      setfooditem(response.data);
    })
    .catch((error) => {
      console.error("There was an error fetching the food items!", error);
    });
}, []);
  return (
    <div>
        <h1>Foodlist</h1>
            
        

          {fooditem.map((item) => (
            <div className="card">
          <li key={item.id}>Food :  {item.food_name}</li>
          <li> Category : {item.category}</li>
          <li> Price : {item.price}</li>
          </div>
        ))}
        </div>  
    
  )
};

export default Foodlist;
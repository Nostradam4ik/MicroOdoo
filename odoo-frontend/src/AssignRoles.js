import React, { useState } from "react";
import axios from "axios";

const AssignRoles = () => {
  // État local pour l’ID utilisateur et les groupes à ajouter
  const [userId, setUserId] = useState("");
  const [groups, setGroups] = useState("");

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Transformation de la chaîne en tableau de nombres
    const groupList = groups.split(",").map(Number);

    try {
      // Envoi des groupes à ajouter à l’utilisateur via l’API
      await axios.post(`http://localhost:8000/users/${userId}/roles`, groupList);
      alert("Groupes ajoutés !");
    } catch (err) {
      console.error(err);
      alert("Erreur !");
    }
  };

  return (
    <div>
      <h2>Attribuer des Rôles</h2>
      <form onSubmit={handleSubmit}>
        <label>ID utilisateur :</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} required />

        <label>Groupes à ajouter (ex: 1,2,3) :</label>
        <input value={groups} onChange={(e) => setGroups(e.target.value)} required />

        <button type="submit">Attribuer</button>
      </form>
    </div>
  );
};

export default AssignRoles;
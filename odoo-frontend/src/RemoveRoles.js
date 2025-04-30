import React, { useState } from "react";
import axios from "axios";

const RemoveRoles = () => {
  const [userId, setUserId] = useState("");  // ID utilisateur
  const [groups, setGroups] = useState("");  // Groupes à retirer

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    const groupList = groups.split(",").map(Number); // Conversion en tableau d’entiers
    try {
      // Appel DELETE avec le corps (body) contenant les IDs de groupes
      await axios.delete(`http://localhost:8000/users/${userId}/roles`, {
        data: groupList
      });
      alert("Groupes retirés !");
    } catch (err) {
      console.error(err);
      alert("Erreur !");
    }
  };

  return (
    <div>
      <h2>Retirer des Rôles</h2>
      <form onSubmit={handleSubmit}>
        <label>ID utilisateur :</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} required />

        <label>Groupes à retirer (ex: 1,2,3) :</label>
        <input value={groups} onChange={(e) => setGroups(e.target.value)} required />

        <button type="submit">Retirer</button>
      </form>
    </div>
  );
};

export default RemoveRoles;
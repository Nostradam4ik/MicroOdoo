import React, { useState } from "react";
import axios from "axios";

const ListRoles = () => {
  const [userId, setUserId] = useState(""); // ID de l’utilisateur
  const [roles, setRoles] = useState([]);   // Groupes associés

  // Envoi de la requête pour récupérer les rôles d’un utilisateur
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.get(`http://localhost:8000/users/${userId}/roles`);
      setRoles(res.data.groups); // Résultat : liste des groupes
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la récupération !");
    }
  };

  return (
    <div>
      <h2>Voir les Groupes d’un Utilisateur</h2>
      <form onSubmit={handleSubmit}>
        <label>ID utilisateur :</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} required />
        <button type="submit">Afficher</button>
      </form>

      {/* Affichage conditionnel des groupes */}
      {roles.length > 0 && (
        <div>
          <h3>Groupes :</h3>
          <ul>
            {roles.map((id) => (
              <li key={id}>Groupe ID : {id}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ListRoles;
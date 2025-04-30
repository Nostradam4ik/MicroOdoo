import React, { useState } from "react";
import axios from "axios";

const DeleteUser = () => {
  // État pour l'ID utilisateur à supprimer
  const [userId, setUserId] = useState("");

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.delete(`http://localhost:8000/users/${userId}`);
      alert("Utilisateur supprimé !");
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la suppression !");
    }
  };

  return (
    <div>
      <h2>Supprimer un Utilisateur</h2>
      <form onSubmit={handleSubmit}>
        <label>ID utilisateur :</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} required />
        <button type="submit">Supprimer</button>
      </form>
    </div>
  );
};

export default DeleteUser;
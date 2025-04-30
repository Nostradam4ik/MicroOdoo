import React, { useState } from "react";
import axios from "axios";

const GetUserId = () => {
  // État pour le login saisi et l'ID récupéré
  const [login, setLogin] = useState("");
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState("");

  // Requête pour récupérer l’ID par login
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.get(`http://localhost:8000/users/get_id_by_login`, {
        params: { login }
      });
      if (res.data.id) {
        setUserId(res.data.id);
        setError("");
      } else {
        setUserId(null);
        setError(res.data.error || "Erreur inconnue");
      }
    } catch (err) {
      console.error(err);
      setError("Erreur lors de la requête.");
    }
  };

  return (
    <div>
      <h2>🔍 Trouver l’ID d’un utilisateur</h2>
      <form onSubmit={handleSubmit}>
        <label>Login :</label>
        <input value={login} onChange={(e) => setLogin(e.target.value)} required />
        <button type="submit">Rechercher</button>
      </form>

      {/* Résultats affichés dynamiquement */}
      {userId && <p>ID de l'utilisateur : <strong>{userId}</strong></p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default GetUserId;
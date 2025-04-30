import React, { useState } from "react";
import axios from "axios";

const UpdateUser = () => {
  const [userId, setUserId] = useState(""); // ID de l’utilisateur à modifier

  // Formulaire de mise à jour utilisateur
  const [formData, setFormData] = useState({
    login_name: "",
    password: "",
    display_name: "",
    groups: "",
  });

  // Mise à jour des champs
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Envoi du formulaire de mise à jour
  const handleSubmit = async (e) => {
    e.preventDefault();
    const groupsArray = formData.groups.split(",").map(Number); // Conversion des groupes

    try {
      await axios.put(`http://localhost:8000/users/${userId}`, {
        login_name: formData.login_name,
        password: formData.password,
        other_ids: { display_name: formData.display_name },
        groups: groupsArray,
      });
      alert("Utilisateur mis à jour !");
    } catch (err) {
      console.error(err);
      alert("Erreur !");
    }
  };

  return (
    <div>
      <h2>Modifier un Utilisateur</h2>
      <form onSubmit={handleSubmit}>
        <label>ID utilisateur :</label>
        <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} required />

        <label>Nom :</label>
        <input name="display_name" value={formData.display_name} onChange={handleChange} required />

        <label>Login :</label>
        <input name="login_name" value={formData.login_name} onChange={handleChange} required />

        <label>Mot de passe :</label>
        <input name="password" type="password" value={formData.password} onChange={handleChange} required />

        <label>Groupes (IDs, ex: 1,2) :</label>
        <input name="groups" value={formData.groups} onChange={handleChange} />

        <button type="submit">Mettre à jour</button>
      </form>
    </div>
  );
};

export default UpdateUser;
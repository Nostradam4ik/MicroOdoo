import React, { useState } from "react";
import axios from "axios";

const CreateUser = () => {
  // État local pour le formulaire utilisateur
  const [formData, setFormData] = useState({
    login_name: "",
    password: "",
    display_name: "",
    groups: "",
  });

  // Message de confirmation ou erreur
  const [message, setMessage] = useState("");

  // Mise à jour du formulaire
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setMessage("");
  };

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Traitement des groupes en tableau d'entiers
    const groupsArray = formData.groups
      .split(",")
      .map((x) => x.trim())
      .filter((x) => x !== "")
      .map(Number)
      .filter((x) => !isNaN(x));

    // Structure du JSON à envoyer
    const payload = {
      login_name: formData.login_name,
      password: formData.password,
      groups: groupsArray,
      other_ids: {
        display_name: formData.display_name,
      },
    };

    console.log("✅ JSON envoyé :", payload); // Debug

    try {
      const response = await axios.post("http://localhost:8000/users/", payload);
      setMessage(`✅ Utilisateur créé avec ID : ${response.data.user_id}`);
    } catch (error) {
      console.error("❌ Erreur backend :", error.response?.data || error.message);
      const detail = error.response?.data?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail.map((e) => e.msg || JSON.stringify(e)).join(", ")
            : JSON.stringify(detail);
      setMessage("❌ Erreur lors de la création : " + message);
    }
  };

  return (
    <div>
      <h2>Créer un Utilisateur</h2>
      <form onSubmit={handleSubmit}>
        <label>Nom complet :</label>
        <input
          name="display_name"
          onChange={handleChange}
          value={formData.display_name}
          placeholder="ex: Andrii Zhmuryk"
          required
        />

        <label>Login :</label>
        <input
          name="login_name"
          onChange={handleChange}
          value={formData.login_name}
          placeholder="ex: andrii.zhmuryk@iutcv.fr"
          required
        />

        <label>Mot de passe :</label>
        <input
          type="password"
          name="password"
          onChange={handleChange}
          value={formData.password}
          required
        />

        <label>Groupes (IDs séparés par des virgules) :</label>
        <input
          name="groups"
          onChange={handleChange}
          value={formData.groups}
          placeholder="ex: 5,6"
        />

        <button type="submit">Créer</button>
      </form>

      {/* Affichage du message de réponse */}
      {message && (
        <p style={{ marginTop: "10px", color: message.startsWith("✅") ? "green" : "red" }}>
          {message}
        </p>
      )}
    </div>
  );
};

export default CreateUser;
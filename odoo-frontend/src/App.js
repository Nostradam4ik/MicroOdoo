// === Import des modules React et composants nécessaires ===
import React, { useState } from "react";
import { Container, Tabs, Tab } from "react-bootstrap";  // Composants Bootstrap pour UI en onglets

// Importation des composants personnalisés pour chaque action
import CreateUser from "./CreateUser";
import UpdateUser from "./UpdateUser";
import DeleteUser from "./DeleteUser";
import AssignRoles from "./AssignRoles";
import RemoveRoles from "./RemoveRoles";
import ListRoles from "./ListRoles";
import GetUserId from "./GetUserId";

// Composant principal de l'application
function App() {
  // État pour suivre l’onglet actif
  const [key, setKey] = useState("create");

  return (
    <Container className="mt-4">
      {/* Titre principal centré */}
      <h1 className="mb-4 text-center">⚙️ Gestion des Utilisateurs Odoo</h1>

      {/* Onglets pour naviguer entre les différentes actions */}
      <Tabs
        activeKey={key}                 // Onglet actif
        onSelect={(k) => setKey(k)}     // Mise à jour de l’état au clic
        className="mb-3"
        justify                        // Répartition égale des onglets
      >
        {/* Onglet pour créer un utilisateur */}
        <Tab eventKey="create" title="Créer">
          <CreateUser />
        </Tab>

        {/* Onglet pour modifier un utilisateur */}
        <Tab eventKey="update" title="Modifier">
          <UpdateUser />
        </Tab>

        {/* Onglet pour supprimer un utilisateur */}
        <Tab eventKey="delete" title="Supprimer">
          <DeleteUser />
        </Tab>

        {/* Onglet pour attribuer des rôles */}
        <Tab eventKey="assign" title="Attribuer Rôles">
          <AssignRoles />
        </Tab>

        {/* Onglet pour retirer des rôles */}
        <Tab eventKey="remove" title="Retirer Rôles">
          <RemoveRoles />
        </Tab>

        {/* Onglet pour lister les rôles d’un utilisateur */}
        <Tab eventKey="list" title="Lister Rôles">
          <ListRoles />
        </Tab>

        {/* Onglet pour récupérer l’ID d’un utilisateur via son login */}
        <Tab eventKey="getid" title="Trouver ID">
          <GetUserId />
        </Tab>
      </Tabs>
    </Container>
  );
}

export default App;
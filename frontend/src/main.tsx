import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./App";
import { DashboardPage } from "./pages/DashboardPage";
import { IrrigationPage } from "./pages/IrrigationPage";
import { MlPage } from "./pages/MlPage";
import { PlantDetailPage } from "./pages/PlantDetailPage";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/plants/:id" element={<PlantDetailPage />} />
          <Route path="/irrigation" element={<IrrigationPage />} />
          <Route path="/ml" element={<MlPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import MainLayout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import Consumables from "./pages/Consumables";
import Purchases from "./pages/Purchases";
import Borrows from "./pages/Borrows";
import Picks from "./pages/Picks";
import Transfers from "./pages/Transfers";
import Statistics from "./pages/Statistics";
import Logs from "./pages/Logs";
import Categories from "./pages/Categories";
import Suppliers from "./pages/Suppliers";
import Help from "./pages/Help";

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="assets" element={<Assets />} />
              <Route path="consumables" element={<Consumables />} />
              <Route path="purchases" element={<Purchases />} />
              <Route path="borrows" element={<Borrows />} />
              <Route path="picks" element={<Picks />} />
              <Route path="transfers" element={<Transfers />} />
              <Route path="statistics" element={<Statistics />} />
              <Route path="logs" element={<Logs />} />
              <Route path="categories" element={<Categories />} />
              <Route path="suppliers" element={<Suppliers />} />
              <Route path="help" element={<Help />} />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;

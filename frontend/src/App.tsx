import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProvedorAutenticacao } from "./context/ContextoAutenticacao";
import RotaPrivada from "./components/RotaPrivada";
import Layout from "./components/Layout";
import PaginaLogin from "./pages/PaginaLogin";
import PaginaPainel from "./pages/PaginaPainel";
import PaginaCadastro from "./pages/PaginaCadastro";
import PaginaHistorico from "./pages/PaginaHistorico";
import type { JSX } from "react";

export default function App(): JSX.Element {
    return (
        <ProvedorAutenticacao>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<PaginaLogin />} />
                    <Route
                        element={
                            <RotaPrivada>
                                <Layout />
                            </RotaPrivada>
                        }
                    >
                        <Route path="/dashboard" element={<PaginaPainel />} />
                        <Route path="/cadastro" element={<PaginaCadastro />} />
                        <Route
                            path="/historico"
                            element={<PaginaHistorico />}
                        />
                    </Route>
                    <Route
                        path="*"
                        element={<Navigate to="/dashboard" replace />}
                    />
                </Routes>
            </BrowserRouter>
        </ProvedorAutenticacao>
    );
}

import { Navigate } from "react-router-dom";
import { useAutenticacao } from "../context/useAutenticacao";
import type { JSX, ReactNode } from "react";

interface RotaPrivadaProps {
    children: ReactNode;
}

export default function RotaPrivada({
    children,
}: RotaPrivadaProps): JSX.Element {
    const { isAuthenticated } = useAutenticacao();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}

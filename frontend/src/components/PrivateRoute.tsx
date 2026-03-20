import { Navigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { JSX, ReactNode } from "react";

interface PrivateRouteProps {
    children: ReactNode;
}

export default function PrivateRoute({
    children,
}: PrivateRouteProps): JSX.Element {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}

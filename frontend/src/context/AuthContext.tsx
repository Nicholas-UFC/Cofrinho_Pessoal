import { useState, useCallback, type ReactNode, type JSX } from "react";
import { jwtDecode } from "jwt-decode";
import { login as apiLogin } from "../api/auth";
import { AuthContext } from "./useAuth";

interface JwtPayload {
    username: string;
    is_staff: boolean;
    exp: number;
}

function getInitialState(): {
    isAuthenticated: boolean;
    username: string | null;
    isAdmin: boolean;
} {
    const token = localStorage.getItem("access");
    if (!token) {
        return { isAuthenticated: false, username: null, isAdmin: false };
    }
    try {
        const decoded = jwtDecode<JwtPayload>(token);
        if (decoded.exp * 1000 < Date.now()) {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            return { isAuthenticated: false, username: null, isAdmin: false };
        }
        return {
            isAuthenticated: true,
            username: decoded.username,
            isAdmin: decoded.is_staff,
        };
    } catch {
        return { isAuthenticated: false, username: null, isAdmin: false };
    }
}

export function AuthProvider({
    children,
}: {
    children: ReactNode;
}): JSX.Element {
    const initial = getInitialState();
    const [isAuthenticated, setIsAuthenticated] = useState(
        initial.isAuthenticated,
    );
    const [username, setUsername] = useState<string | null>(initial.username);
    const [isAdmin, setIsAdmin] = useState(initial.isAdmin);

    const login = useCallback(
        async (user: string, password: string): Promise<void> => {
            const tokens = await apiLogin(user, password);
            localStorage.setItem("access", tokens.access);
            localStorage.setItem("refresh", tokens.refresh);
            const decoded = jwtDecode<JwtPayload>(tokens.access);
            setIsAuthenticated(true);
            setUsername(decoded.username);
            setIsAdmin(decoded.is_staff);
        },
        [],
    );

    const logout = useCallback((): void => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        setIsAuthenticated(false);
        setUsername(null);
        setIsAdmin(false);
    }, []);

    return (
        <AuthContext.Provider
            value={{ isAuthenticated, username, isAdmin, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}

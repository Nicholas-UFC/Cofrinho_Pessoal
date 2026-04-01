import { useState, useCallback, type ReactNode, type JSX } from "react";
import { login as apiLogin, logout as apiLogout } from "../api/autenticacao";
import { ContextoAutenticacao } from "./useAutenticacao";

interface UsuarioInfo {
    username: string;
    isAdmin: boolean;
}

// Armazena apenas info do usuário (não o token) para persistir UI entre reloads.
// O token vive exclusivamente no cookie httpOnly — OWASP prática 76.
function salvarInfoUsuario(info: UsuarioInfo): void {
    localStorage.setItem("usuario_info", JSON.stringify(info));
}

function limparInfoUsuario(): void {
    localStorage.removeItem("usuario_info");
}

function getInitialState(): {
    isAuthenticated: boolean;
    username: string | null;
    isAdmin: boolean;
} {
    const raw = localStorage.getItem("usuario_info");
    if (!raw)
        return { isAuthenticated: false, username: null, isAdmin: false };
    try {
        const { username, isAdmin } = JSON.parse(raw) as UsuarioInfo;
        return { isAuthenticated: true, username, isAdmin };
    } catch {
        return { isAuthenticated: false, username: null, isAdmin: false };
    }
}

export function ProvedorAutenticacao({
    children,
}: {
    children: ReactNode;
}): JSX.Element {
    const initial = getInitialState();
    const [isAuthenticated, setIsAuthenticated] = useState(
        initial.isAuthenticated,
    );
    const [username, setUsername] = useState(initial.username);
    const [isAdmin, setIsAdmin] = useState(initial.isAdmin);

    const login = useCallback(
        async (user: string, password: string): Promise<void> => {
            const { username: nome, is_staff: isStaff } = await apiLogin(
                user,
                password,
            );
            salvarInfoUsuario({ username: nome, isAdmin: isStaff });
            setIsAuthenticated(true);
            setUsername(nome);
            setIsAdmin(isStaff);
        },
        [],
    );

    const logout = useCallback(async (): Promise<void> => {
        try {
            await apiLogout();
        } catch {
            // Mesmo com erro, limpa o estado local.
        }
        limparInfoUsuario();
        setIsAuthenticated(false);
        setUsername(null);
        setIsAdmin(false);
    }, []);

    return (
        <ContextoAutenticacao.Provider
            value={{ isAuthenticated, username, isAdmin, login, logout }}
        >
            {children}
        </ContextoAutenticacao.Provider>
    );
}

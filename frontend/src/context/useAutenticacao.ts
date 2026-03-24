import { createContext, useContext } from "react";

export interface AuthContextValue {
    isAuthenticated: boolean;
    username: string | null;
    isAdmin: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
}

export const ContextoAutenticacao = createContext<AuthContextValue | null>(
    null,
);

export function useAutenticacao(): AuthContextValue {
    const ctx = useContext(ContextoAutenticacao);
    if (!ctx) {
        throw new Error(
            "useAutenticacao must be used within ProvedorAutenticacao",
        );
    }
    return ctx;
}

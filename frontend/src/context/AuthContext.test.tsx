import { describe, it, expect } from "vitest";
import { screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { useAuth } from "./useAuth";
import type { JSX } from "react";

// ──────────────────────────────────────────────────────
// Helper — exibe o estado do contexto na tela
// ──────────────────────────────────────────────────────
function AuthDisplay(): JSX.Element {
    const { isAuthenticated, username, isAdmin } = useAuth();
    return (
        <div>
            <span data-testid="auth">
                {isAuthenticated ? "autenticado" : "anonimo"}
            </span>
            <span data-testid="username">{username ?? "nenhum"}</span>
            <span data-testid="admin">{isAdmin ? "admin" : "normal"}</span>
        </div>
    );
}

function LogoutButton(): JSX.Element {
    const { logout } = useAuth();
    return <button onClick={logout}>Sair</button>;
}

// ──────────────────────────────────────────────────────
// Estado inicial
// ──────────────────────────────────────────────────────
describe("AuthContext — estado inicial", () => {
    it("sem token no localStorage → usuário anônimo", () => {
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
        expect(screen.getByTestId("username")).toHaveTextContent("nenhum");
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });

    it("token válido no localStorage → usuário autenticado", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("autenticado");
        expect(screen.getByTestId("username")).toHaveTextContent("testuser");
    });

    it("token válido com is_staff=true → isAdmin verdadeiro", () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("admin");
    });

    it("token válido com is_staff=false → isAdmin falso", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });
});

// ──────────────────────────────────────────────────────
// Login
// ──────────────────────────────────────────────────────
describe("AuthContext — login", () => {
    it("login bem-sucedido salva tokens no localStorage", async () => {
        function LoginButton(): JSX.Element {
            const { login } = useAuth();
            return (
                <button
                    onClick={() => {
                        void login("admin", "admin123");
                    }}
                >
                    Entrar
                </button>
            );
        }

        renderWithProviders(<LoginButton />);
        await userEvent.click(screen.getByText("Entrar"));

        expect(localStorage.getItem("access")).not.toBeNull();
        expect(localStorage.getItem("refresh")).not.toBeNull();
    });

    it("login bem-sucedido atualiza isAuthenticated para true", async () => {
        function LoginAndDisplay(): JSX.Element {
            const { login, isAuthenticated } = useAuth();
            return (
                <div>
                    <button
                        onClick={() => {
                            void login("admin", "admin123");
                        }}
                    >
                        Entrar
                    </button>
                    <span data-testid="auth">
                        {isAuthenticated ? "autenticado" : "anonimo"}
                    </span>
                </div>
            );
        }

        renderWithProviders(<LoginAndDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");

        await userEvent.click(screen.getByText("Entrar"));

        expect(screen.getByTestId("auth")).toHaveTextContent("autenticado");
    });

    it("login bem-sucedido define o username correto", async () => {
        function LoginAndDisplay(): JSX.Element {
            const { login, username } = useAuth();
            return (
                <div>
                    <button
                        onClick={() => {
                            void login("admin", "admin123");
                        }}
                    >
                        Entrar
                    </button>
                    <span data-testid="username">{username ?? "nenhum"}</span>
                </div>
            );
        }

        renderWithProviders(<LoginAndDisplay />);
        await userEvent.click(screen.getByText("Entrar"));

        expect(screen.getByTestId("username")).toHaveTextContent("testuser");
    });
});

// ──────────────────────────────────────────────────────
// Logout
// ──────────────────────────────────────────────────────
describe("AuthContext — logout", () => {
    it("logout remove access do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<LogoutButton />);
        await userEvent.click(screen.getByText("Sair"));
        expect(localStorage.getItem("access")).toBeNull();
    });

    it("logout remove refresh do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<LogoutButton />);
        await userEvent.click(screen.getByText("Sair"));
        expect(localStorage.getItem("refresh")).toBeNull();
    });

    it("logout redefine isAuthenticated para false", async () => {
        localStorage.setItem("access", makeFakeToken());

        function LogoutDisplay(): JSX.Element {
            const { logout, isAuthenticated } = useAuth();
            return (
                <div>
                    <button onClick={logout}>Sair</button>
                    <span data-testid="auth">
                        {isAuthenticated ? "autenticado" : "anonimo"}
                    </span>
                </div>
            );
        }

        renderWithProviders(<LogoutDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("autenticado");
        await act(async () => {
            await userEvent.click(screen.getByText("Sair"));
        });
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
    });

    it("logout redefine username para null", async () => {
        localStorage.setItem("access", makeFakeToken());

        function LogoutDisplay(): JSX.Element {
            const { logout, username } = useAuth();
            return (
                <div>
                    <button onClick={logout}>Sair</button>
                    <span data-testid="username">{username ?? "nenhum"}</span>
                </div>
            );
        }

        renderWithProviders(<LogoutDisplay />);
        await act(async () => {
            await userEvent.click(screen.getByText("Sair"));
        });
        expect(screen.getByTestId("username")).toHaveTextContent("nenhum");
    });

    it("logout redefine isAdmin para false", async () => {
        localStorage.setItem("access", makeFakeToken(true));

        function LogoutDisplay(): JSX.Element {
            const { logout, isAdmin } = useAuth();
            return (
                <div>
                    <button onClick={logout}>Sair</button>
                    <span data-testid="admin">
                        {isAdmin ? "admin" : "normal"}
                    </span>
                </div>
            );
        }

        renderWithProviders(<LogoutDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("admin");
        await act(async () => {
            await userEvent.click(screen.getByText("Sair"));
        });
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });
});

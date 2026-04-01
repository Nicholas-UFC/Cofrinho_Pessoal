import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { useAutenticacao } from "./useAutenticacao";
import type { JSX } from "react";

/*
 * ContextoAutenticacao — testes de estado inicial e login
 * --------------------------------------------------------
 *
 * O ContextoAutenticacao lê o 'usuario_info' do localStorage na inicialização.
 * O token JWT vive exclusivamente no cookie httpOnly (OWASP prática 76) e
 * nunca é armazenado no localStorage.
 *
 * Esta suíte cobre dois grupos:
 *
 * 1. ESTADO INICIAL: ausência de usuario_info → anônimo; com usuario_info
 *    → autenticado com username e isAdmin corretos.
 *
 * 2. LOGIN: MSW intercepta /api/token/ retornando { username, is_staff }.
 *    Verifica que usuario_info é salvo, isAuthenticated muda e username
 *    é preenchido.
 */

function AuthDisplay(): JSX.Element {
    const { isAuthenticated, username, isAdmin } = useAutenticacao();
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

describe("ContextoAutenticacao — estado inicial", () => {
    it("sem usuario_info no localStorage → usuário anônimo", () => {
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
        expect(screen.getByTestId("username")).toHaveTextContent("nenhum");
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });

    it("usuario_info no localStorage → usuário autenticado", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("autenticado");
        expect(screen.getByTestId("username")).toHaveTextContent("testuser");
    });

    it("usuario_info com isAdmin=true → isAdmin verdadeiro", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: true }),
        );
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("admin");
    });

    it("usuario_info com isAdmin=false → isAdmin falso", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });
});

describe("ContextoAutenticacao — login", () => {
    it("login bem-sucedido salva usuario_info no localStorage", async () => {
        function LoginButton(): JSX.Element {
            const { login } = useAutenticacao();
            return (
                <button onClick={() => void login("admin", "admin123")}>
                    Entrar
                </button>
            );
        }

        renderWithProviders(<LoginButton />);
        await userEvent.click(screen.getByText("Entrar"));

        const info = localStorage.getItem("usuario_info");
        expect(info).not.toBeNull();
        expect(JSON.parse(info ?? "{}").username).toBe("testuser");
    });

    it("login bem-sucedido atualiza isAuthenticated para true", async () => {
        function LoginAndDisplay(): JSX.Element {
            const { login, isAuthenticated } = useAutenticacao();
            return (
                <div>
                    <button onClick={() => void login("admin", "admin123")}>
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
            const { login, username } = useAutenticacao();
            return (
                <div>
                    <button onClick={() => void login("admin", "admin123")}>
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

import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { useAutenticacao } from "./useAutenticacao";
import type { JSX } from "react";

/*
 * ContextoAutenticacao — testes de estado inicial e login
 * --------------------------------------------------------
 *
 * O ContextoAutenticacao é o coração da autenticação do frontend.
 * Ele lê o token JWT do localStorage na inicialização, decodifica o
 * payload (sem nenhuma chamada à API) e expõe `isAuthenticated`,
 * `username` e `isAdmin` para todos os componentes filhos.
 *
 * Esta suíte cobre dois grupos de comportamento:
 *
 * 1. ESTADO INICIAL: o que o contexto expõe ao montar sem interação
 *    do usuário. Os cenários cobrem: ausência de token, token de
 *    usuário comum (is_staff=false) e token de administrador
 *    (is_staff=true). Isso garante que a UI já nasce no estado
 *    correto — sem precisar de nenhum round-trip ao servidor.
 *
 * 2. LOGIN: o que acontece quando o usuário submete credenciais
 *    válidas. O MSW intercepta a chamada ao endpoint de token e
 *    devolve um access + refresh token. Os testes verificam que:
 *    — os tokens são salvos no localStorage (para persistência),
 *    — `isAuthenticated` muda para true (para liberar rotas privadas),
 *    — `username` é preenchido a partir do payload do JWT.
 *
 * Os testes de logout ficam em ContextoAutenticacao.logout.test.tsx
 * para manter cada arquivo com uma única responsabilidade.
 */

// ──────────────────────────────────────────────────────
// Helper — exibe o estado do contexto na tela
// ──────────────────────────────────────────────────────
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

// ──────────────────────────────────────────────────────
// Estado inicial
// ──────────────────────────────────────────────────────
describe("ContextoAutenticacao — estado inicial", () => {
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
describe("ContextoAutenticacao — login", () => {
    it("login bem-sucedido salva tokens no localStorage", async () => {
        function LoginButton(): JSX.Element {
            const { login } = useAutenticacao();
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
            const { login, isAuthenticated } = useAutenticacao();
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
            const { login, username } = useAutenticacao();
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

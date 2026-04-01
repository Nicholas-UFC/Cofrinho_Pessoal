import { describe, it, expect, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

// ---------------------------------------------------------------------------
// App — testes de roteamento
//
// App usa BrowserRouter internamente, que lê window.location.
// Cada teste usa window.history.pushState para navegar antes de renderizar.
// O afterEach reseta a URL para "/" para não vazar entre testes.
// ---------------------------------------------------------------------------

afterEach(() => {
    window.history.pushState({}, "", "/");
});

describe("App — roteamento público", () => {
    it("/ sem autenticação exibe a tela de login", async () => {
        render(<App />);
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /entrar na conta/i }),
            ).toBeInTheDocument();
        });
    });

    it("/login renderiza o formulário de autenticação", async () => {
        window.history.pushState({}, "", "/login");
        render(<App />);
        await waitFor(() => {
            expect(screen.getByLabelText(/usuário/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
        });
    });

    it("rota inexistente redireciona para /dashboard e cai no login", async () => {
        window.history.pushState({}, "", "/pagina-que-nao-existe");
        render(<App />);
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /entrar na conta/i }),
            ).toBeInTheDocument();
        });
    });
});

describe("App — rotas protegidas sem autenticação", () => {
    it("/dashboard sem token redireciona para /login", async () => {
        window.history.pushState({}, "", "/dashboard");
        render(<App />);
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /entrar na conta/i }),
            ).toBeInTheDocument();
        });
    });

    it("/cadastro sem token redireciona para /login", async () => {
        window.history.pushState({}, "", "/cadastro");
        render(<App />);
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /entrar na conta/i }),
            ).toBeInTheDocument();
        });
    });

    it("/historico sem token redireciona para /login", async () => {
        window.history.pushState({}, "", "/historico");
        render(<App />);
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /entrar na conta/i }),
            ).toBeInTheDocument();
        });
    });
});

describe("App — rotas protegidas com autenticação", () => {
    it("/dashboard com token renderiza o PaginaPainel", async () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        window.history.pushState({}, "", "/dashboard");
        render(<App />);
        await waitFor(
            () => {
                expect(
                    screen.getByText("Total de Entradas"),
                ).toBeInTheDocument();
            },
            { timeout: 5000 },
        );
    });

    it("/cadastro com token renderiza o PaginaCadastro", async () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        window.history.pushState({}, "", "/cadastro");
        render(<App />);
        await waitFor(
            () => {
                // PaginaCadastro tem as abas Gasto, Entrada, Categoria, Fonte
                expect(screen.getByText("Fonte")).toBeInTheDocument();
            },
            { timeout: 5000 },
        );
    });

    it("/historico com token renderiza o PaginaHistorico", async () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        window.history.pushState({}, "", "/historico");
        render(<App />);
        await waitFor(
            () => {
                expect(screen.getByText("Mercado")).toBeInTheDocument();
            },
            { timeout: 5000 },
        );
    });
});

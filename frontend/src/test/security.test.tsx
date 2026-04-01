import { describe, it, expect } from "vitest";
import { screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "./utils";
import { server } from "./server";
import type { JSX } from "react";
import { useAutenticacao } from "../context/useAutenticacao";

/*
 * Testes de segurança do frontend — autenticação e controle de acesso
 * -------------------------------------------------------------------
 *
 * O token JWT vive no cookie httpOnly (OWASP prática 76) e nunca é
 * armazenado no localStorage. O localStorage guarda apenas 'usuario_info'
 * com { username, isAdmin } para persistir o estado da UI entre reloads.
 */

function AuthDisplay(): JSX.Element {
    const { isAuthenticated, isAdmin } = useAutenticacao();
    return (
        <div>
            <span data-testid="auth">
                {isAuthenticated ? "autenticado" : "anonimo"}
            </span>
            <span data-testid="admin">{isAdmin ? "admin" : "normal"}</span>
        </div>
    );
}

function infoUsuario(isAdmin = false): void {
    localStorage.setItem(
        "usuario_info",
        JSON.stringify({ username: "testuser", isAdmin }),
    );
}

// ──────────────────────────────────────────────────────
// Testes de segurança — estado de autenticação
// ──────────────────────────────────────────────────────
describe("Segurança — estado de autenticação", () => {
    it("sem usuario_info no localStorage → usuário anônimo", () => {
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
    });

    it("usuario_info com isAdmin=false não é tratado como admin", () => {
        infoUsuario(false);
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });

    it("usuario_info removido após logout", async () => {
        infoUsuario();

        function LogoutButton(): JSX.Element {
            const { logout } = useAutenticacao();
            return <button onClick={() => void logout()}>Sair</button>;
        }

        renderWithProviders(<LogoutButton />);
        await act(async () => {
            await userEvent.click(screen.getByText("Sair"));
        });
        expect(localStorage.getItem("usuario_info")).toBeNull();
    });
});

// ──────────────────────────────────────────────────────
// Testes de segurança — interceptor 401
// ──────────────────────────────────────────────────────
describe("Segurança — interceptor 401", () => {
    it("remove usuario_info quando refresh falha após 401", async () => {
        infoUsuario();

        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
            ),
            http.post("http://localhost:8000/api/token/refresh/", () =>
                HttpResponse.json(
                    { detail: "Token inválido" },
                    { status: 401 },
                ),
            ),
        );

        const { getResumo } = await import("../api/financas");
        try {
            await getResumo();
        } catch {
            // Esperado falhar — o importante é o efeito colateral
        }

        await waitFor(() => {
            expect(localStorage.getItem("usuario_info")).toBeNull();
        });
    });
});

// ──────────────────────────────────────────────────────
// Testes de segurança — XSS
// ──────────────────────────────────────────────────────
describe("Segurança — XSS", () => {
    it("dados da API com HTML não são interpretados como markup", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({
                    count: 1,
                    next: null,
                    previous: null,
                    results: [
                        {
                            id: 1,
                            descricao: "<script>alert('xss')</script>",
                            valor: "10.00",
                            data: "2026-03-01",
                            categoria: 1,
                            categoria_nome: "<b>bold</b>",
                        },
                    ],
                }),
            ),
        );

        const { default: PaginaHistorico } =
            await import("../pages/PaginaHistorico");

        renderWithProviders(<PaginaHistorico />);

        await waitFor(() => {
            expect(
                screen.getByText("<script>alert('xss')</script>"),
            ).toBeInTheDocument();
        });

        const scripts = document.querySelectorAll("script");
        scripts.forEach((s) => {
            expect(s.textContent).not.toContain("alert('xss')");
        });
    });
});

// ──────────────────────────────────────────────────────
// Testes de segurança — controle de acesso admin
// ──────────────────────────────────────────────────────
describe("Segurança — acesso admin", () => {
    it("link do Painel Admin não aparece para usuários normais", () => {
        infoUsuario(false);

        function TopBarMock(): JSX.Element {
            const { isAdmin } = useAutenticacao();
            return (
                <div>
                    {isAdmin && <a href="/admin/">Painel Admin</a>}
                    <span>Menu</span>
                </div>
            );
        }

        renderWithProviders(<TopBarMock />);
        expect(screen.queryByText("Painel Admin")).not.toBeInTheDocument();
    });

    it("link do Painel Admin aparece apenas para admins", () => {
        infoUsuario(true);

        function TopBarMock(): JSX.Element {
            const { isAdmin } = useAutenticacao();
            return <div>{isAdmin && <a href="/admin/">Painel Admin</a>}</div>;
        }

        renderWithProviders(<TopBarMock />);
        expect(screen.getByText("Painel Admin")).toBeInTheDocument();
    });
});

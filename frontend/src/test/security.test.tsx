import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "./utils";
import { makeFakeToken, makeExpiredToken } from "./handlers";
import { server } from "./server";
import type { JSX } from "react";
import { useAutenticacao } from "../context/useAutenticacao";

// ──────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────
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

// ──────────────────────────────────────────────────────
// Testes de segurança — tokens
// ──────────────────────────────────────────────────────
describe("Segurança — tokens", () => {
    it("token expirado no localStorage não autentica o usuário", () => {
        localStorage.setItem("access", makeExpiredToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });

    it("token malformado/corrompido não autentica o usuário", () => {
        localStorage.setItem("access", "isto.nao.e.um.jwt");
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
    });

    it("token com is_staff false não é tratado como admin", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });

    it("tokens são removidos do localStorage após logout", () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");

        function LogoutButton(): JSX.Element {
            const { logout } = useAutenticacao();
            return <button onClick={logout}>Sair</button>;
        }

        const { getByText } = renderWithProviders(<LogoutButton />);
        getByText("Sair").click();

        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });
});

// ──────────────────────────────────────────────────────
// Testes de segurança — interceptor 401
// ──────────────────────────────────────────────────────
describe("Segurança — interceptor 401", () => {
    it("remove tokens quando refresh falha após 401", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "invalid-refresh");

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

        // Importa a função de API para disparar o interceptor diretamente
        const { getResumo } = await import("../api/financas");
        try {
            await getResumo();
        } catch {
            // Esperado falhar — o importante é o efeito colateral nos tokens
        }

        await waitFor(() => {
            expect(localStorage.getItem("access")).toBeNull();
            expect(localStorage.getItem("refresh")).toBeNull();
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
            // O texto bruto deve aparecer — não executado como HTML
            expect(
                screen.getByText("<script>alert('xss')</script>"),
            ).toBeInTheDocument();
        });

        // Nenhum script extra deve ter sido injetado pelo conteúdo da API
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
        localStorage.setItem("access", makeFakeToken(false));

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
        localStorage.setItem("access", makeFakeToken(true));

        function TopBarMock(): JSX.Element {
            const { isAdmin } = useAutenticacao();
            return <div>{isAdmin && <a href="/admin/">Painel Admin</a>}</div>;
        }

        renderWithProviders(<TopBarMock />);
        expect(screen.getByText("Painel Admin")).toBeInTheDocument();
    });
});

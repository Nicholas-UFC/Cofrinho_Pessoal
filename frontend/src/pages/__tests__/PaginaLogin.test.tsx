import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../../test/utils";
import { makeFakeToken } from "../../test/handlers";
import { server } from "../../test/server";
import PaginaLogin from "../PaginaLogin";
import type { JSX } from "react";

/*
 * PaginaLogin — testes do formulário de autenticação
 * ---------------------------------------------------
 *
 * A PaginaLogin é a porta de entrada da aplicação. Ela exibe um
 * formulário de usuário e senha, faz a chamada ao endpoint de token
 * JWT e, em caso de sucesso, redireciona para /dashboard. Se o
 * usuário já estiver autenticado (token válido no localStorage), deve
 * ser redirecionado imediatamente sem ver o formulário.
 *
 * O que é verificado:
 *
 * — Renderização: título, campos de usuário e senha, e botão Entrar
 *   estão presentes na tela.
 *
 * — Fluxo feliz: após preencher credenciais válidas e submeter, o
 *   MSW retorna os tokens e o componente redireciona para /dashboard.
 *
 * — Credenciais inválidas: quando o endpoint retorna 401, a mensagem
 *   "credenciais inválidas" é exibida abaixo do formulário — sem
 *   redirecionar nem travar a tela.
 *
 * — Já autenticado: se o localStorage já contém um token válido ao
 *   montar a página, o React Router redireciona para /dashboard
 *   imediatamente, sem exibir o formulário.
 *
 * — Estado de loading: enquanto a requisição está pendente, o botão
 *   exibe "Entrando..." e fica desabilitado para evitar duplo submit.
 */

function DashboardMock(): JSX.Element {
    return <div>Dashboard</div>;
}

function renderLogin(): void {
    renderWithProviders(
        <Routes>
            <Route path="/login" element={<PaginaLogin />} />
            <Route path="/dashboard" element={<DashboardMock />} />
        </Routes>,
        { initialEntries: ["/login"] },
    );
}

describe("PaginaLogin", () => {
    it("renderiza o formulário de login", () => {
        renderLogin();
        expect(
            screen.getByRole("heading", { name: /entrar na conta/i }),
        ).toBeInTheDocument();
        expect(screen.getByLabelText(/usuário/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /entrar/i }),
        ).toBeInTheDocument();
    });

    it("faz login com sucesso e redireciona para /dashboard", async () => {
        renderLogin();
        await userEvent.type(screen.getByLabelText(/usuário/i), "testuser");
        await userEvent.type(screen.getByLabelText(/senha/i), "pass123");
        await userEvent.click(screen.getByRole("button", { name: /entrar/i }));
        await waitFor(() => {
            expect(screen.getByText("Dashboard")).toBeInTheDocument();
        });
    });

    it("exibe mensagem de erro em credenciais inválidas", async () => {
        server.use(
            http.post("http://localhost:8000/api/token/", () =>
                HttpResponse.json(
                    { detail: "No active account found" },
                    { status: 401 },
                ),
            ),
        );
        renderLogin();
        await userEvent.type(screen.getByLabelText(/usuário/i), "errado");
        await userEvent.type(screen.getByLabelText(/senha/i), "errado");
        await userEvent.click(screen.getByRole("button", { name: /entrar/i }));
        await waitFor(() => {
            expect(
                screen.getByText(/credenciais inválidas/i),
            ).toBeInTheDocument();
        });
    });

    it("redireciona para /dashboard se já autenticado", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(
            <Routes>
                <Route path="/login" element={<PaginaLogin />} />
                <Route path="/dashboard" element={<DashboardMock />} />
            </Routes>,
            { initialEntries: ["/login"] },
        );
        await waitFor(() => {
            expect(screen.getByText("Dashboard")).toBeInTheDocument();
        });
    });

    it("exibe 'Entrando...' durante o carregamento", async () => {
        // Handler com atraso para capturar o estado de loading
        server.use(
            http.post("http://localhost:8000/api/token/", async () => {
                await new Promise<void>((resolve) => {
                    setTimeout(resolve, 100);
                });
                return HttpResponse.json({
                    access: makeFakeToken(),
                    refresh: "fake-refresh",
                });
            }),
        );
        renderLogin();
        await userEvent.type(screen.getByLabelText(/usuário/i), "testuser");
        await userEvent.type(screen.getByLabelText(/senha/i), "pass123");
        await userEvent.click(screen.getByRole("button", { name: /entrar/i }));
        expect(
            screen.getByRole("button", { name: /entrando/i }),
        ).toBeDisabled();
        await waitFor(() => {
            expect(screen.getByText("Dashboard")).toBeInTheDocument();
        });
    });
});

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

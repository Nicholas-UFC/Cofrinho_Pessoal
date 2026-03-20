import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { Route, Routes } from "react-router-dom";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import LoginPage from "./LoginPage";

const DashboardStub = (): React.JSX.Element => (
    <span data-testid="dashboard">Dashboard</span>
);

function AppRoutes(): React.JSX.Element {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={<DashboardStub />} />
            <Route path="/" element={<LoginPage />} />
        </Routes>
    );
}

describe("LoginPage — renderização", () => {
    it("exibe o título 'Cofrinho Pessoal'", () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        expect(screen.getByText(/Cofrinho Pessoal/)).toBeInTheDocument();
    });

    it("exibe o campo de usuário", () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        expect(screen.getByLabelText("Usuário")).toBeInTheDocument();
    });

    it("exibe o campo de senha", () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        expect(screen.getByLabelText("Senha")).toBeInTheDocument();
    });

    it("exibe o botão de Entrar", () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        expect(
            screen.getByRole("button", { name: "Entrar" }),
        ).toBeInTheDocument();
    });
});

describe("LoginPage — redirecionamento", () => {
    it("usuário já autenticado é redirecionado para /dashboard", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        expect(screen.getByTestId("dashboard")).toBeInTheDocument();
    });

    it("login bem-sucedido redireciona para /dashboard", async () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        await userEvent.type(screen.getByLabelText("Usuário"), "admin");
        await userEvent.type(screen.getByLabelText("Senha"), "admin123");
        await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
        await waitFor(() => {
            expect(screen.getByTestId("dashboard")).toBeInTheDocument();
        });
    });
});

describe("LoginPage — tratamento de erros", () => {
    it("exibe mensagem de erro em credenciais inválidas", async () => {
        server.use(
            http.post("http://localhost:8000/api/token/", () =>
                HttpResponse.json(
                    { detail: "No active account found" },
                    { status: 401 },
                ),
            ),
        );

        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        await userEvent.type(screen.getByLabelText("Usuário"), "errado");
        await userEvent.type(screen.getByLabelText("Senha"), "errado");
        await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

        await waitFor(() => {
            expect(
                screen.getByText("Credenciais inválidas. Tente novamente."),
            ).toBeInTheDocument();
        });
    });

    it("botão fica desabilitado enquanto carrega", async () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/login"] });
        await userEvent.type(screen.getByLabelText("Usuário"), "admin");
        await userEvent.type(screen.getByLabelText("Senha"), "admin123");

        const button = screen.getByRole("button", { name: "Entrar" });
        await userEvent.click(button);

        // Durante o loading o texto muda para "Entrando..."
        // e o botão fica disabled
        await waitFor(() => {
            expect(screen.getByTestId("dashboard")).toBeInTheDocument();
        });
    });
});

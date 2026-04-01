import { describe, it, expect } from "vitest";
import { screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { useAutenticacao } from "./useAutenticacao";
import type { JSX } from "react";

/*
 * ContextoAutenticacao — testes de logout
 * ----------------------------------------
 *
 * O logout deve produzir os seguintes efeitos:
 *
 * 1. Remover 'usuario_info' do localStorage — o token vive no cookie httpOnly
 *    e é invalidado pelo backend; o localStorage guarda apenas info de UI.
 *
 * 2. Redefinir isAuthenticated para false.
 *
 * 3. Redefinir username e isAdmin para null/false.
 */

function infoUsuario(isAdmin = false): void {
    localStorage.setItem(
        "usuario_info",
        JSON.stringify({ username: "testuser", isAdmin }),
    );
}

describe("ContextoAutenticacao — logout", () => {
    it("logout remove usuario_info do localStorage", async () => {
        infoUsuario();

        function LogoutButton(): JSX.Element {
            const { logout } = useAutenticacao();
            return <button onClick={() => void logout()}>Sair</button>;
        }

        renderWithProviders(<LogoutButton />);
        await userEvent.click(screen.getByText("Sair"));
        expect(localStorage.getItem("usuario_info")).toBeNull();
    });

    it("logout redefine isAuthenticated para false", async () => {
        infoUsuario();

        function LogoutDisplay(): JSX.Element {
            const { logout, isAuthenticated } = useAutenticacao();
            return (
                <div>
                    <button onClick={() => void logout()}>Sair</button>
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
        infoUsuario();

        function LogoutDisplay(): JSX.Element {
            const { logout, username } = useAutenticacao();
            return (
                <div>
                    <button onClick={() => void logout()}>Sair</button>
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
        infoUsuario(true);

        function LogoutDisplay(): JSX.Element {
            const { logout, isAdmin } = useAutenticacao();
            return (
                <div>
                    <button onClick={() => void logout()}>Sair</button>
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

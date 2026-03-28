import { describe, it, expect } from "vitest";
import { screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { useAutenticacao } from "./useAutenticacao";
import type { JSX } from "react";

/*
 * ContextoAutenticacao — testes de logout
 * ----------------------------------------
 *
 * Esta suíte foca exclusivamente no comportamento do logout, separada do
 * arquivo principal para manter cada arquivo com uma única responsabilidade.
 *
 * O logout deve produzir quatro efeitos simultâneos e imediatos:
 *
 * 1. Remover o `access` token do localStorage — impede que qualquer
 *    chamada à API subsequente seja autenticada.
 *
 * 2. Remover o `refresh` token do localStorage — impede que o interceptor
 *    do axios tente renovar o acesso automaticamente.
 *
 * 3. Redefinir `isAuthenticated` para false — todas as RotaPrivadas devem
 *    imediatamente redirecionar para /login sem precisar recarregar a página.
 *
 * 4. Redefinir `username` para null e `isAdmin` para false — limpa qualquer
 *    estado residual do usuário anterior, evitando que um novo usuário que
 *    faça login no mesmo browser veja dados do usuário anterior.
 *
 * Cada teste usa um componente helper inline que expõe o estado relevante
 * via `data-testid`, permitindo verificar o estado antes e depois do logout.
 */

describe("ContextoAutenticacao — logout", () => {
    it("logout remove access do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");

        function LogoutButton(): JSX.Element {
            const { logout } = useAutenticacao();
            return <button onClick={logout}>Sair</button>;
        }

        renderWithProviders(<LogoutButton />);
        await userEvent.click(screen.getByText("Sair"));
        expect(localStorage.getItem("access")).toBeNull();
    });

    it("logout remove refresh do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");

        function LogoutButton(): JSX.Element {
            const { logout } = useAutenticacao();
            return <button onClick={logout}>Sair</button>;
        }

        renderWithProviders(<LogoutButton />);
        await userEvent.click(screen.getByText("Sair"));
        expect(localStorage.getItem("refresh")).toBeNull();
    });

    it("logout redefine isAuthenticated para false", async () => {
        localStorage.setItem("access", makeFakeToken());

        function LogoutDisplay(): JSX.Element {
            const { logout, isAuthenticated } = useAutenticacao();
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
            const { logout, username } = useAutenticacao();
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
            const { logout, isAdmin } = useAutenticacao();
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

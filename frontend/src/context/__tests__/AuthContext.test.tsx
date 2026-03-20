import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../test/utils";
import { makeFakeToken } from "../../test/handlers";
import { useAuth } from "../useAuth";
import type { JSX } from "react";

function AuthDisplay(): JSX.Element {
    const { isAuthenticated, username, isAdmin, login, logout } = useAuth();
    return (
        <div>
            <span data-testid="auth">
                {isAuthenticated ? "autenticado" : "anonimo"}
            </span>
            <span data-testid="username">{username ?? "nenhum"}</span>
            <span data-testid="admin">{isAdmin ? "admin" : "normal"}</span>
            <button
                onClick={() => {
                    void login("testuser", "pass123");
                }}
            >
                Login
            </button>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

describe("AuthContext", () => {
    it("inicia como anônimo quando não há token no localStorage", () => {
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
        expect(screen.getByTestId("username")).toHaveTextContent("nenhum");
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });

    it("inicia como autenticado quando há token válido no localStorage", () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("auth")).toHaveTextContent("autenticado");
        expect(screen.getByTestId("username")).toHaveTextContent("testuser");
    });

    it("faz login e atualiza o estado", async () => {
        renderWithProviders(<AuthDisplay />);
        await userEvent.click(screen.getByText("Login"));
        await waitFor(() => {
            expect(screen.getByTestId("auth")).toHaveTextContent(
                "autenticado",
            );
        });
        expect(screen.getByTestId("username")).toHaveTextContent("testuser");
        expect(localStorage.getItem("access")).not.toBeNull();
        expect(localStorage.getItem("refresh")).not.toBeNull();
    });

    it("faz logout e limpa o estado e o localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<AuthDisplay />);
        await userEvent.click(screen.getByText("Logout"));
        expect(screen.getByTestId("auth")).toHaveTextContent("anonimo");
        expect(screen.getByTestId("username")).toHaveTextContent("nenhum");
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });

    it("reconhece usuário admin pelo campo is_staff do token", () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("admin");
    });

    it("não autentica usuário normal como admin", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<AuthDisplay />);
        expect(screen.getByTestId("admin")).toHaveTextContent("normal");
    });
});

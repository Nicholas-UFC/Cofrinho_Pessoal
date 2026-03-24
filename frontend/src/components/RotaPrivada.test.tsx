import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import RotaPrivada from "./RotaPrivada";

const Protected = (): React.JSX.Element => (
    <span data-testid="protected">Conteúdo protegido</span>
);
const LoginStub = (): React.JSX.Element => (
    <span data-testid="login">Página de login</span>
);

function AppRoutes(): React.JSX.Element {
    return (
        <Routes>
            <Route path="/login" element={<LoginStub />} />
            <Route
                path="/"
                element={
                    <RotaPrivada>
                        <Protected />
                    </RotaPrivada>
                }
            />
        </Routes>
    );
}

describe("RotaPrivada", () => {
    it("redireciona para /login quando não autenticado", () => {
        renderWithProviders(<AppRoutes />, { initialEntries: ["/"] });
        expect(screen.getByTestId("login")).toBeInTheDocument();
        expect(screen.queryByTestId("protected")).not.toBeInTheDocument();
    });

    it("renderiza o conteúdo protegido quando autenticado", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<AppRoutes />, { initialEntries: ["/"] });
        expect(screen.getByTestId("protected")).toBeInTheDocument();
        expect(screen.queryByTestId("login")).not.toBeInTheDocument();
    });

    it("não expõe o conteúdo protegido sem token válido", () => {
        localStorage.setItem("access", "token.invalido.qualquer");
        renderWithProviders(<AppRoutes />, { initialEntries: ["/"] });
        expect(screen.queryByTestId("protected")).not.toBeInTheDocument();
    });
});

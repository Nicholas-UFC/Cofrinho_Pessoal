import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { renderWithProviders } from "../../test/utils";
import { makeFakeToken } from "../../test/handlers";
import RotaPrivada from "../RotaPrivada";
import type { JSX } from "react";

function Protected(): JSX.Element {
    return <div>Conteúdo protegido</div>;
}

function LoginMock(): JSX.Element {
    return <div>Página de login</div>;
}

function renderRoutes(authenticated: boolean): void {
    if (authenticated) {
        localStorage.setItem("access", makeFakeToken());
    }
    renderWithProviders(
        <Routes>
            <Route path="/login" element={<LoginMock />} />
            <Route
                path="/"
                element={
                    <RotaPrivada>
                        <Protected />
                    </RotaPrivada>
                }
            />
        </Routes>,
        { initialEntries: ["/"] },
    );
}

describe("RotaPrivada", () => {
    it("redireciona para /login quando não autenticado", () => {
        renderRoutes(false);
        expect(screen.getByText("Página de login")).toBeInTheDocument();
        expect(
            screen.queryByText("Conteúdo protegido"),
        ).not.toBeInTheDocument();
    });

    it("renderiza o conteúdo protegido quando autenticado", () => {
        renderRoutes(true);
        expect(screen.getByText("Conteúdo protegido")).toBeInTheDocument();
        expect(screen.queryByText("Página de login")).not.toBeInTheDocument();
    });
});

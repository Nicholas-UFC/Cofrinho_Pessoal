import { describe, it, expect } from "vitest";
import { render, waitFor } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ProvedorAutenticacao } from "../context/ContextoAutenticacao";
import PaginaLogin from "../pages/PaginaLogin";
import BarraTopo from "../components/BarraTopo";
import MenuLateral from "../components/MenuLateral";
import { FormularioCategoriaFonte } from "../components/formularios/FormularioCategoriaFonte";
import { makeFakeToken } from "./handlers";
import type { JSX } from "react";

expect.extend(toHaveNoViolations);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderComProviders(ui: JSX.Element): ReturnType<typeof render> {
    return render(
        <MemoryRouter initialEntries={["/"]}>
            <ProvedorAutenticacao>{ui}</ProvedorAutenticacao>
        </MemoryRouter>,
    );
}

function renderLogin(): ReturnType<typeof render> {
    return render(
        <MemoryRouter initialEntries={["/login"]}>
            <ProvedorAutenticacao>
                <Routes>
                    <Route path="/login" element={<PaginaLogin />} />
                    <Route path="/dashboard" element={<div>Painel</div>} />
                </Routes>
            </ProvedorAutenticacao>
        </MemoryRouter>,
    );
}

// ---------------------------------------------------------------------------
// Testes de acessibilidade — axe-core via jest-axe
// ---------------------------------------------------------------------------

describe("Acessibilidade — PaginaLogin", () => {
    it("não tem violações de acessibilidade", async () => {
        const { container } = renderLogin();
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});

describe("Acessibilidade — BarraTopo", () => {
    it("não tem violações de acessibilidade", async () => {
        localStorage.setItem("access", makeFakeToken());
        const { container } = renderComProviders(
            <BarraTopo onMenuClick={() => undefined} />,
        );
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});

describe("Acessibilidade — MenuLateral", () => {
    it("não tem violações de acessibilidade (fechado)", async () => {
        localStorage.setItem("access", makeFakeToken());
        const { container } = renderComProviders(
            <MenuLateral open={false} onClose={() => undefined} />,
        );
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });

    it("não tem violações de acessibilidade (aberto)", async () => {
        localStorage.setItem("access", makeFakeToken());
        const { container } = renderComProviders(
            <MenuLateral open={true} onClose={() => undefined} />,
        );
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});

describe("Acessibilidade — FormularioCategoriaFonte", () => {
    it("não tem violações de acessibilidade na aba categoria", async () => {
        localStorage.setItem("access", makeFakeToken());
        const { container } = renderComProviders(
            <FormularioCategoriaFonte
                activeTab="categoria"
                loading={false}
                success={null}
                error={null}
                onSubmit={() => undefined}
            />,
        );
        await waitFor(() => {
            // espera o componente estabilizar
        });
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});

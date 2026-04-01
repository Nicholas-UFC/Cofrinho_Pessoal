import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProvedorAutenticacao } from "../../context/ContextoAutenticacao";
import Layout from "../Layout";

import type { ReactNode } from "react";

// ---------------------------------------------------------------------------
// Helper — renderiza Layout dentro de um Router com autenticação
// ---------------------------------------------------------------------------

function renderLayout(outlet: ReactNode = <div>Conteúdo de Teste</div>): void {
    render(
        <MemoryRouter initialEntries={["/"]}>
            <ProvedorAutenticacao>
                <Routes>
                    <Route element={<Layout />}>
                        <Route path="/" element={outlet} />
                    </Route>
                </Routes>
            </ProvedorAutenticacao>
        </MemoryRouter>,
    );
}

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

describe("Layout", () => {
    it("renderiza o conteúdo do Outlet", () => {
        renderLayout(<div>Conteúdo Exclusivo</div>);
        expect(screen.getByText("Conteúdo Exclusivo")).toBeInTheDocument();
    });

    it("renderiza a BarraTopo com o botão de abrir menu", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        expect(
            screen.getByRole("button", { name: /abrir menu/i }),
        ).toBeInTheDocument();
    });

    it("renderiza o MenuLateral com navegação", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        expect(screen.getByRole("navigation")).toBeInTheDocument();
    });

    it("MenuLateral exibe links de navegação", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        expect(screen.getByText("Dashboard")).toBeInTheDocument();
        expect(screen.getByText("Cadastro")).toBeInTheDocument();
        expect(screen.getByText("Histórico")).toBeInTheDocument();
    });

    it("overlay não está visível antes de abrir o menu", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        expect(document.querySelector('[aria-hidden="true"]')).toBeNull();
    });

    it("exibe overlay ao clicar no botão de abrir menu", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        fireEvent.click(screen.getByRole("button", { name: /abrir menu/i }));
        expect(
            document.querySelector('[aria-hidden="true"]'),
        ).toBeInTheDocument();
    });

    it("fecha o overlay ao clicar nele", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();

        fireEvent.click(screen.getByRole("button", { name: /abrir menu/i }));
        const overlay = document.querySelector('[aria-hidden="true"]');
        expect(overlay).toBeInTheDocument();

        if (overlay) fireEvent.click(overlay);
        expect(document.querySelector('[aria-hidden="true"]')).toBeNull();
    });

    it("exibe o nome do usuário autenticado na BarraTopo", () => {
        localStorage.setItem(
            "usuario_info",
            JSON.stringify({ username: "testuser", isAdmin: false }),
        );
        renderLayout();
        expect(screen.getByText("testuser")).toBeInTheDocument();
    });
});

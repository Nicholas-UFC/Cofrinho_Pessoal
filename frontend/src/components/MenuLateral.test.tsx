import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import MenuLateral from "./MenuLateral";

const defaultProps = { open: true, onClose: vi.fn() };

describe("MenuLateral — navegação", () => {
    it("exibe o link Dashboard", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("exibe o link Cadastro", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        expect(screen.getByText("Cadastro")).toBeInTheDocument();
    });

    it("exibe o link Histórico", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        expect(screen.getByText("Histórico")).toBeInTheDocument();
    });

    it("link Dashboard aponta para /dashboard", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        const link = screen.getByText("Dashboard").closest("a");
        expect(link?.getAttribute("href")).toBe("/dashboard");
    });

    it("link Cadastro aponta para /cadastro", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        const link = screen.getByText("Cadastro").closest("a");
        expect(link?.getAttribute("href")).toBe("/cadastro");
    });

    it("link Histórico aponta para /historico", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        const link = screen.getByText("Histórico").closest("a");
        expect(link?.getAttribute("href")).toBe("/historico");
    });
});

describe("MenuLateral — logout", () => {
    it("exibe botão de Logout", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral {...defaultProps} />);
        expect(screen.getByText("Logout")).toBeInTheDocument();
    });

    it("botão Logout limpa os tokens do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<MenuLateral {...defaultProps} />);
        await userEvent.click(screen.getByText("Logout"));
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });
});

describe("MenuLateral — mobile", () => {
    it("exibe botão de fechar no mobile", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral open={true} onClose={vi.fn()} />);
        expect(screen.getByLabelText("Fechar menu")).toBeInTheDocument();
    });

    it("botão fechar chama onClose", async () => {
        localStorage.setItem("access", makeFakeToken());
        const onClose = vi.fn();
        renderWithProviders(<MenuLateral open={true} onClose={onClose} />);
        await userEvent.click(screen.getByLabelText("Fechar menu"));
        expect(onClose).toHaveBeenCalledOnce();
    });

    it("clicar em link de navegação chama onClose", async () => {
        localStorage.setItem("access", makeFakeToken());
        const onClose = vi.fn();
        renderWithProviders(<MenuLateral open={true} onClose={onClose} />);
        await userEvent.click(screen.getByText("Dashboard"));
        expect(onClose).toHaveBeenCalled();
    });

    it("aplica -translate-x-full quando fechado (drawer escondido no mobile)", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral open={false} onClose={vi.fn()} />);
        const aside = screen.getByRole("complementary", {
            name: "Menu de navegação",
        });
        expect(aside.className).toContain("-translate-x-full");
    });

    it("aplica translate-x-0 quando aberto (drawer visível no mobile)", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<MenuLateral open={true} onClose={vi.fn()} />);
        const aside = screen.getByRole("complementary", {
            name: "Menu de navegação",
        });
        expect(aside.className).not.toContain("-translate-x-full");
        expect(aside.className).toContain("translate-x-0");
    });
});

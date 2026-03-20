import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import TopBar from "./TopBar";

const defaultProps = { onMenuClick: vi.fn() };

describe("TopBar — exibição do usuário", () => {
    it("exibe o nome do usuário logado", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        expect(screen.getByText("testuser")).toBeInTheDocument();
    });

    it("exibe a saudação 'Olá,'", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        expect(screen.getByText(/Olá,/)).toBeInTheDocument();
    });
});

describe("TopBar — dropdown do usuário", () => {
    it("dropdown não está visível por padrão", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        expect(screen.queryByText("Logout")).not.toBeInTheDocument();
    });

    it("clique no botão abre o dropdown com Logout", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.getByText("Logout")).toBeInTheDocument();
    });

    it("segundo clique no botão fecha o dropdown", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.queryByText("Logout")).not.toBeInTheDocument();
    });
});

describe("TopBar — Painel Admin", () => {
    it("não exibe link 'Painel Admin' para usuário normal", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.queryByText("Painel Admin")).not.toBeInTheDocument();
    });

    it("exibe link 'Painel Admin' para admin", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.getByText("Painel Admin")).toBeInTheDocument();
    });

    it("link 'Painel Admin' aponta para /admin/", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        const link = screen.getByText("Painel Admin").closest("a");
        expect(link?.href).toContain("/admin/");
    });

    it("link 'Painel Admin' abre em nova aba (target=_blank)", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        const link = screen.getByText("Painel Admin").closest("a");
        expect(link?.target).toBe("_blank");
        expect(link?.rel).toContain("noopener");
    });
});

describe("TopBar — logout", () => {
    it("botão Logout limpa tokens do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<TopBar {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        await userEvent.click(screen.getByText("Logout"));
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });
});

describe("TopBar — mobile", () => {
    it("exibe botão hambúrguer", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<TopBar {...defaultProps} />);
        expect(screen.getByLabelText("Abrir menu")).toBeInTheDocument();
    });

    it("botão hambúrguer chama onMenuClick", async () => {
        localStorage.setItem("access", makeFakeToken());
        const onMenuClick = vi.fn();
        renderWithProviders(<TopBar onMenuClick={onMenuClick} />);
        await userEvent.click(screen.getByLabelText("Abrir menu"));
        expect(onMenuClick).toHaveBeenCalledOnce();
    });
});

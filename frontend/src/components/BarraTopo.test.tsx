import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import BarraTopo from "./BarraTopo";

/*
 * BarraTopo — testes do cabeçalho da aplicação
 * ---------------------------------------------
 *
 * A BarraTopo é o componente de cabeçalho que aparece em todas as
 * páginas autenticadas. Ela exibe o nome do usuário logado, um
 * dropdown de ações (logout e, para admins, link para o Painel
 * Admin do Django) e o botão hambúrguer para abrir o MenuLateral
 * no mobile.
 *
 * Os testes são divididos em cinco grupos:
 *
 * 1. EXIBIÇÃO DO USUÁRIO: o nome extraído do JWT é exibido ao lado
 *    da saudação "Olá,".
 *
 * 2. DROPDOWN: o dropdown está oculto por padrão e abre ao clicar no
 *    nome do usuário. Um segundo clique fecha o dropdown — toggle.
 *
 * 3. PAINEL ADMIN: o link "Painel Admin" só aparece quando `isAdmin`
 *    é true (is_staff=true no payload JWT). Para usuários comuns, o
 *    link não deve existir no DOM. Quando exibido, deve apontar para
 *    /admin/ e abrir em nova aba com rel="noopener" por segurança.
 *
 * 4. LOGOUT: clicar em Logout no dropdown limpa ambos os tokens do
 *    localStorage.
 *
 * 5. MOBILE: o botão hambúrguer ("Abrir menu") está presente e, ao
 *    ser clicado, chama a prop `onMenuClick` para que o componente
 *    pai (Layout) possa abrir o MenuLateral.
 */

const defaultProps = { onMenuClick: vi.fn() };

describe("BarraTopo — exibição do usuário", () => {
    it("exibe o nome do usuário logado", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        expect(screen.getByText("testuser")).toBeInTheDocument();
    });

    it("exibe a saudação 'Olá,'", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        expect(screen.getByText(/Olá,/)).toBeInTheDocument();
    });
});

describe("BarraTopo — dropdown do usuário", () => {
    it("dropdown não está visível por padrão", () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        expect(screen.queryByText("Logout")).not.toBeInTheDocument();
    });

    it("clique no botão abre o dropdown com Logout", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.getByText("Logout")).toBeInTheDocument();
    });

    it("segundo clique no botão fecha o dropdown", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.queryByText("Logout")).not.toBeInTheDocument();
    });
});

describe("BarraTopo — Painel Admin", () => {
    it("não exibe link 'Painel Admin' para usuário normal", async () => {
        localStorage.setItem("access", makeFakeToken(false));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.queryByText("Painel Admin")).not.toBeInTheDocument();
    });

    it("exibe link 'Painel Admin' para admin", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        expect(screen.getByText("Painel Admin")).toBeInTheDocument();
    });

    it("link 'Painel Admin' aponta para /admin/", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        const link = screen.getByText("Painel Admin").closest("a");
        expect(link?.href).toContain("/admin/");
    });

    it("link 'Painel Admin' abre em nova aba (target=_blank)", async () => {
        localStorage.setItem("access", makeFakeToken(true));
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        const link = screen.getByText("Painel Admin").closest("a");
        expect(link?.target).toBe("_blank");
        expect(link?.rel).toContain("noopener");
    });
});

describe("BarraTopo — logout", () => {
    it("botão Logout limpa tokens do localStorage", async () => {
        localStorage.setItem("access", makeFakeToken());
        localStorage.setItem("refresh", "fake-refresh");
        renderWithProviders(<BarraTopo {...defaultProps} />);
        await userEvent.click(screen.getByText("testuser"));
        await userEvent.click(screen.getByText("Logout"));
        expect(localStorage.getItem("access")).toBeNull();
        expect(localStorage.getItem("refresh")).toBeNull();
    });
});

describe("BarraTopo — mobile", () => {
    it("exibe botão hambúrguer", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<BarraTopo {...defaultProps} />);
        expect(screen.getByLabelText("Abrir menu")).toBeInTheDocument();
    });

    it("botão hambúrguer chama onMenuClick", async () => {
        localStorage.setItem("access", makeFakeToken());
        const onMenuClick = vi.fn();
        renderWithProviders(<BarraTopo onMenuClick={onMenuClick} />);
        await userEvent.click(screen.getByLabelText("Abrir menu"));
        expect(onMenuClick).toHaveBeenCalledOnce();
    });
});

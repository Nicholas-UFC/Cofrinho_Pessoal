import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import PaginaCadastro from "./PaginaCadastro";

async function renderCadastro(): Promise<void> {
    localStorage.setItem("access", makeFakeToken());
    renderWithProviders(<PaginaCadastro />);
    // Aguarda as categorias e fontes serem carregadas
    await waitFor(() => {
        expect(screen.getByText("Registrar Gasto")).toBeInTheDocument();
    });
}

describe("PaginaCadastro — abas", () => {
    it("exibe as 4 abas", async () => {
        await renderCadastro();
        // Os botões de aba contêm emoji + label — verifica pelo textContent
        const buttonTexts = screen
            .getAllByRole("button")
            .map((b) => b.textContent);
        ["Gasto", "Entrada", "Categoria", "Fonte"].forEach((label) => {
            expect(buttonTexts.some((t) => t.includes(label))).toBe(true);
        });
    });

    it("aba padrão é Gasto", async () => {
        await renderCadastro();
        expect(screen.getByText("Registrar Gasto")).toBeInTheDocument();
    });

    it("clicar em Entrada exibe formulário de entrada", async () => {
        await renderCadastro();
        await userEvent.click(
            screen.getByRole("button", { name: /entrada/i }),
        );
        expect(screen.getByText("Registrar Entrada")).toBeInTheDocument();
    });

    it("clicar em Categoria exibe formulário de categoria", async () => {
        await renderCadastro();
        await userEvent.click(
            screen.getByRole("button", { name: /categoria/i }),
        );
        expect(screen.getByText("Criar Categoria")).toBeInTheDocument();
    });

    it("clicar em Fonte exibe formulário de fonte", async () => {
        await renderCadastro();
        await userEvent.click(screen.getByRole("button", { name: /fonte/i }));
        expect(screen.getByText("Criar Fonte")).toBeInTheDocument();
    });
});

// Regressão: API retornava {count, next, previous, results:[]} para categorias/fontes.
// setCategorias(obj) fazia categorias.map() lançar TypeError, travando /cadastro.
describe("PaginaCadastro — regressão paginação", () => {
    it("não trava quando API retorna categorias como lista plana", async () => {
        await renderCadastro();
        // Se categorias não forem lista, a renderização lança exceção antes disso.
        // O select deve ter opções além do placeholder (categorias populadas).
        const categoriaSelect = screen.getByLabelText("Categoria");
        const options = Array.from(categoriaSelect.querySelectorAll("option"));
        expect(options.length).toBeGreaterThan(1);
    });
});

describe("PaginaCadastro — formulário de Gasto", () => {
    it("submit bem-sucedido exibe mensagem de sucesso", async () => {
        await renderCadastro();
        await userEvent.type(screen.getByLabelText("Descrição"), "Mercado");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "50");
        await userEvent.selectOptions(screen.getByLabelText("Categoria"), "1");
        await userEvent.click(screen.getByText("Registrar Gasto"));
        await waitFor(() => {
            expect(
                screen.getByText("Gasto registrado com sucesso!"),
            ).toBeInTheDocument();
        });
    });

    it("erro da API exibe mensagem de erro", async () => {
        server.use(
            http.post("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json(
                    { descricao: ["Este campo não pode ser em branco."] },
                    { status: 400 },
                ),
            ),
        );

        await renderCadastro();
        await userEvent.type(screen.getByLabelText("Descrição"), "x");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "10");
        await userEvent.selectOptions(screen.getByLabelText("Categoria"), "1");
        await userEvent.click(screen.getByText("Registrar Gasto"));

        await waitFor(() => {
            expect(
                screen.getByText("Este campo não pode ser em branco."),
            ).toBeInTheDocument();
        });
    });
});

describe("PaginaCadastro — formulário de Entrada", () => {
    it("submit bem-sucedido exibe mensagem de sucesso", async () => {
        await renderCadastro();
        await userEvent.click(
            screen.getByRole("button", { name: /entrada/i }),
        );
        await userEvent.type(screen.getByLabelText("Descrição"), "Salário");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "3000");
        await userEvent.selectOptions(screen.getByLabelText("Fonte"), "1");
        await userEvent.click(screen.getByText("Registrar Entrada"));
        await waitFor(() => {
            expect(
                screen.getByText("Entrada registrada com sucesso!"),
            ).toBeInTheDocument();
        });
    });
});

describe("PaginaCadastro — formulário de Categoria", () => {
    it("submit bem-sucedido exibe mensagem de sucesso", async () => {
        await renderCadastro();
        await userEvent.click(
            screen.getByRole("button", { name: /categoria/i }),
        );
        await userEvent.type(
            screen.getByLabelText(/Nome da Categoria/),
            "Lazer",
        );
        await userEvent.click(screen.getByText("Criar Categoria"));
        await waitFor(() => {
            expect(
                screen.getByText("Categoria criada com sucesso!"),
            ).toBeInTheDocument();
        });
    });
});

describe("PaginaCadastro — formulário de Fonte", () => {
    it("submit bem-sucedido exibe mensagem de sucesso", async () => {
        await renderCadastro();
        await userEvent.click(screen.getByRole("button", { name: /fonte/i }));
        await userEvent.type(
            screen.getByLabelText(/Nome da Fonte/),
            "Bradesco",
        );
        await userEvent.click(screen.getByText("Criar Fonte"));
        await waitFor(() => {
            expect(
                screen.getByText("Fonte criada com sucesso!"),
            ).toBeInTheDocument();
        });
    });
});

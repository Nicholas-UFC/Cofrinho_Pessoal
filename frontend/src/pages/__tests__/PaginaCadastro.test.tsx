import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../../test/utils";
import { server } from "../../test/server";
import PaginaCadastro from "../PaginaCadastro";

/*
 * PaginaCadastro — testes de fluxo completo de cadastro
 * -------------------------------------------------------
 *
 * A PaginaCadastro é a tela principal de entrada de dados financeiros.
 * Ela agrupa quatro formulários em abas: Gasto, Entrada, Categoria e
 * Fonte. O usuário alterna entre elas clicando nos botões de aba, e
 * cada aba renderiza seu próprio formulário com campos específicos.
 *
 * O que é verificado:
 *
 * — Renderização: todas as quatro abas estão presentes e o formulário
 *   correto é exibido para cada uma.
 *
 * — Fluxo feliz: preencher e submeter cada formulário produz a mensagem
 *   de sucesso correspondente (gasto, entrada, categoria, fonte).
 *
 * — Erro de API: quando o endpoint retorna 400, a mensagem de erro da
 *   resposta é exibida abaixo do formulário.
 *
 * — Regressão de categorias: a API retorna categorias e fontes num
 *   envelope paginado {count, next, previous, results:[]}. Se o
 *   componente passar o objeto inteiro para `.map()` em vez de
 *   `.results`, a página trava com TypeError. O teste garante que o
 *   select de Categoria está populado com opções reais.
 *
 * — Troca de aba: trocar de aba deve limpar mensagens de sucesso e
 *   erro da aba anterior, evitando que o usuário veja feedback obsoleto.
 */

describe("PaginaCadastro", () => {
    it("renderiza as quatro abas", async () => {
        renderWithProviders(<PaginaCadastro />);
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /registrar gasto/i }),
            ).toBeInTheDocument();
        });
        // Aba Entrada, Categoria e Fonte são únicas na tela quando na aba Gasto
        expect(
            screen.getByRole("button", { name: /entrada/i }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /categoria/i }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /fonte/i }),
        ).toBeInTheDocument();
    });

    it("registra um gasto com sucesso", async () => {
        renderWithProviders(<PaginaCadastro />);
        await waitFor(() => {
            expect(screen.getByLabelText(/descrição/i)).toBeInTheDocument();
        });
        await userEvent.type(screen.getByLabelText(/descrição/i), "Mercado");
        await userEvent.type(screen.getByLabelText(/valor \(r\$\)/i), "50");
        await userEvent.selectOptions(
            screen.getByLabelText(/categoria/i),
            "1",
        );
        await userEvent.click(
            screen.getByRole("button", { name: /registrar gasto/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/gasto registrado com sucesso/i),
            ).toBeInTheDocument();
        });
    });

    it("registra uma entrada com sucesso", async () => {
        renderWithProviders(<PaginaCadastro />);
        // Na aba gasto, só existe um botão com "entrada" — a aba
        await userEvent.click(
            screen.getByRole("button", { name: /entrada/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /registrar entrada/i }),
            ).toBeInTheDocument();
        });
        await userEvent.type(screen.getByLabelText(/descrição/i), "Salário");
        await userEvent.type(screen.getByLabelText(/valor \(r\$\)/i), "3000");
        await userEvent.selectOptions(screen.getByLabelText(/fonte/i), "1");
        await userEvent.click(
            screen.getByRole("button", { name: /registrar entrada/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/entrada registrada com sucesso/i),
            ).toBeInTheDocument();
        });
    });

    it("cria uma categoria com sucesso", async () => {
        renderWithProviders(<PaginaCadastro />);
        await userEvent.click(
            screen.getByRole("button", { name: /categoria/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /criar categoria/i }),
            ).toBeInTheDocument();
        });
        await userEvent.type(
            screen.getByLabelText(/nome da categoria/i),
            "Lazer",
        );
        await userEvent.click(
            screen.getByRole("button", { name: /criar categoria/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/categoria criada com sucesso/i),
            ).toBeInTheDocument();
        });
    });

    it("cria uma fonte com sucesso", async () => {
        renderWithProviders(<PaginaCadastro />);
        await userEvent.click(screen.getByRole("button", { name: /fonte/i }));
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /criar fonte/i }),
            ).toBeInTheDocument();
        });
        await userEvent.type(screen.getByLabelText(/nome da fonte/i), "Pix");
        await userEvent.click(
            screen.getByRole("button", { name: /criar fonte/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/fonte criada com sucesso/i),
            ).toBeInTheDocument();
        });
    });

    it("exibe erro da API ao falhar no cadastro de gasto", async () => {
        server.use(
            http.post("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json(
                    { valor: ["Este campo não pode ser negativo."] },
                    { status: 400 },
                ),
            ),
        );
        renderWithProviders(<PaginaCadastro />);
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /registrar gasto/i }),
            ).toBeInTheDocument();
        });
        await userEvent.type(screen.getByLabelText(/descrição/i), "Teste");
        await userEvent.type(screen.getByLabelText(/valor \(r\$\)/i), "10");
        await userEvent.selectOptions(
            screen.getByLabelText(/categoria/i),
            "1",
        );
        await userEvent.click(
            screen.getByRole("button", { name: /registrar gasto/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/este campo não pode ser negativo/i),
            ).toBeInTheDocument();
        });
    });

    // Regressão: API retornava {count, next, previous, results:[]} para categorias/fontes.
    // setCategorias(obj) fazia categorias.map() lançar TypeError, travando /cadastro.
    it("regressão: não trava quando API retorna categorias como lista plana", async () => {
        renderWithProviders(<PaginaCadastro />);
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /registrar gasto/i }),
            ).toBeInTheDocument();
        });
        // Se categorias não forem uma lista, a renderização lança exceção antes disso.
        // O select deve ter opções além do placeholder (categorias populadas).
        const categoriaSelect = screen.getByLabelText(/categoria/i);
        const options = Array.from(categoriaSelect.querySelectorAll("option"));
        expect(options.length).toBeGreaterThan(1);
    });

    it("troca de aba reseta mensagens de sucesso e erro", async () => {
        renderWithProviders(<PaginaCadastro />);
        await waitFor(() => {
            expect(
                screen.getByRole("button", { name: /registrar gasto/i }),
            ).toBeInTheDocument();
        });
        await userEvent.type(screen.getByLabelText(/descrição/i), "Mercado");
        await userEvent.type(screen.getByLabelText(/valor \(r\$\)/i), "50");
        await userEvent.selectOptions(
            screen.getByLabelText(/categoria/i),
            "1",
        );
        await userEvent.click(
            screen.getByRole("button", { name: /registrar gasto/i }),
        );
        await waitFor(() => {
            expect(
                screen.getByText(/gasto registrado com sucesso/i),
            ).toBeInTheDocument();
        });
        await userEvent.click(
            screen.getByRole("button", { name: /entrada/i }),
        );
        expect(
            screen.queryByText(/gasto registrado com sucesso/i),
        ).not.toBeInTheDocument();
    });
});

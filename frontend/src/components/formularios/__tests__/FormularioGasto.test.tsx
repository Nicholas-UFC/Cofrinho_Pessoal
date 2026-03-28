import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormularioGasto } from "../FormularioGasto";
import type { Categoria } from "../../../api/financas";

/*
 * FormularioGasto — testes de campos, submit e estados
 * -----------------------------------------------------
 *
 * O FormularioGasto é um componente controlado que recebe a lista de
 * categorias disponíveis via prop e chama `onSubmit` com os quatro
 * campos preenchidos: descrição, valor, data e categoria.
 *
 * Os testes são divididos em três grupos:
 *
 * 1. CAMPOS: os quatro campos obrigatórios (Descrição, Valor, Data e
 *    Categoria) estão presentes com seus respectivos labels. O select
 *    de Categoria exibe as opções recebidas via prop.
 *
 * 2. SUBMIT: ao preencher todos os campos e clicar em "Registrar
 *    Gasto", `onSubmit` é chamado com os valores corretos. Após o
 *    submit, os campos Descrição e Valor são limpos para que o
 *    usuário possa registrar o próximo gasto imediatamente — a data
 *    e a categoria são mantidas para conveniência.
 *
 * 3. ESTADOS: o componente reflete os estados recebidos via props —
 *    durante loading o botão exibe "Salvando..." e fica desabilitado,
 *    e as mensagens de sucesso/erro são exibidas conforme fornecidas
 *    pelo componente pai (PaginaCadastro).
 */

const categorias: Categoria[] = [
    { id: 1, nome: "Alimentação", criado_em: "2026-01-01" },
    { id: 2, nome: "Transporte", criado_em: "2026-01-01" },
];

const propsPadrao = {
    categorias,
    loading: false,
    success: null,
    error: null,
    onSubmit: vi.fn(),
};

describe("FormularioGasto — campos", () => {
    it("exibe os quatro campos do formulário", () => {
        render(<FormularioGasto {...propsPadrao} />);
        expect(screen.getByLabelText("Descrição")).toBeInTheDocument();
        expect(screen.getByLabelText("Valor (R$)")).toBeInTheDocument();
        expect(screen.getByLabelText("Data")).toBeInTheDocument();
        expect(screen.getByLabelText("Categoria")).toBeInTheDocument();
    });

    it("exibe as categorias no select", () => {
        render(<FormularioGasto {...propsPadrao} />);
        expect(
            screen.getByRole("option", { name: "Alimentação" }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("option", { name: "Transporte" }),
        ).toBeInTheDocument();
    });
});

describe("FormularioGasto — submit", () => {
    it("chama onSubmit com os valores preenchidos", async () => {
        const onSubmit = vi.fn();
        render(<FormularioGasto {...propsPadrao} onSubmit={onSubmit} />);

        await userEvent.type(screen.getByLabelText("Descrição"), "Mercado");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "50");
        await userEvent.selectOptions(screen.getByLabelText("Categoria"), "1");
        await userEvent.click(screen.getByText("Registrar Gasto"));

        expect(onSubmit).toHaveBeenCalledWith(
            "Mercado",
            "50",
            expect.any(String),
            "1",
        );
    });

    it("limpa descrição e valor após submit", async () => {
        render(<FormularioGasto {...propsPadrao} />);

        const descricao = screen.getByLabelText("Descrição");
        await userEvent.type(descricao, "Mercado");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "50");
        await userEvent.selectOptions(screen.getByLabelText("Categoria"), "1");
        await userEvent.click(screen.getByText("Registrar Gasto"));

        expect(descricao).toHaveValue("");
        expect(screen.getByLabelText("Valor (R$)")).toHaveValue(null);
    });
});

describe("FormularioGasto — estados", () => {
    it("desabilita o botão e exibe 'Salvando...' durante loading", () => {
        render(<FormularioGasto {...propsPadrao} loading={true} />);
        expect(
            screen.getByRole("button", { name: "Salvando..." }),
        ).toBeDisabled();
    });

    it("exibe mensagem de sucesso quando fornecida", () => {
        render(
            <FormularioGasto
                {...propsPadrao}
                success="Gasto registrado com sucesso!"
            />,
        );
        expect(
            screen.getByText("Gasto registrado com sucesso!"),
        ).toBeInTheDocument();
    });

    it("exibe mensagem de erro quando fornecida", () => {
        render(
            <FormularioGasto
                {...propsPadrao}
                error="Erro ao registrar gasto."
            />,
        );
        expect(
            screen.getByText("Erro ao registrar gasto."),
        ).toBeInTheDocument();
    });
});

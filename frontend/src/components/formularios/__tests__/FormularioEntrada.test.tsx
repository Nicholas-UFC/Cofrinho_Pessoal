import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormularioEntrada } from "../FormularioEntrada";
import type { Fonte } from "../../../api/financas";

/*
 * FormularioEntrada — testes de campos, submit e estados
 * -------------------------------------------------------
 *
 * O FormularioEntrada é o espelho do FormularioGasto para receitas.
 * Ele recebe a lista de fontes disponíveis via prop e chama `onSubmit`
 * com os quatro campos preenchidos: descrição, valor, data e fonte.
 *
 * Os testes são divididos em três grupos:
 *
 * 1. CAMPOS: os quatro campos obrigatórios (Descrição, Valor, Data e
 *    Fonte) estão presentes com seus respectivos labels. O select de
 *    Fonte exibe as opções recebidas via prop.
 *
 * 2. SUBMIT: ao preencher todos os campos e clicar em "Registrar
 *    Entrada", `onSubmit` é chamado com os valores corretos. Após o
 *    submit, os campos Descrição e Valor são limpos — mesma convenção
 *    do FormularioGasto para agilizar cadastros repetidos.
 *
 * 3. ESTADOS: durante loading o botão exibe "Salvando..." e fica
 *    desabilitado para evitar duplo submit. As mensagens de sucesso
 *    e erro são exibidas conforme fornecidas pelo componente pai.
 */

const fontes: Fonte[] = [
    { id: 1, nome: "Salário", criado_em: "2026-01-01" },
    { id: 2, nome: "Nubank", criado_em: "2026-01-01" },
];

const propsPadrao = {
    fontes,
    loading: false,
    success: null,
    error: null,
    onSubmit: vi.fn(),
};

describe("FormularioEntrada — campos", () => {
    it("exibe os quatro campos do formulário", () => {
        render(<FormularioEntrada {...propsPadrao} />);
        expect(screen.getByLabelText("Descrição")).toBeInTheDocument();
        expect(screen.getByLabelText("Valor (R$)")).toBeInTheDocument();
        expect(screen.getByLabelText("Data")).toBeInTheDocument();
        expect(screen.getByLabelText("Fonte")).toBeInTheDocument();
    });

    it("exibe as fontes no select", () => {
        render(<FormularioEntrada {...propsPadrao} />);
        expect(
            screen.getByRole("option", { name: "Salário" }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("option", { name: "Nubank" }),
        ).toBeInTheDocument();
    });
});

describe("FormularioEntrada — submit", () => {
    it("chama onSubmit com os valores preenchidos", async () => {
        const onSubmit = vi.fn();
        render(<FormularioEntrada {...propsPadrao} onSubmit={onSubmit} />);

        await userEvent.type(screen.getByLabelText("Descrição"), "Salário");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "3000");
        await userEvent.selectOptions(screen.getByLabelText("Fonte"), "1");
        await userEvent.click(screen.getByText("Registrar Entrada"));

        expect(onSubmit).toHaveBeenCalledWith(
            "Salário",
            "3000",
            expect.any(String),
            "1",
        );
    });

    it("limpa descrição e valor após submit", async () => {
        render(<FormularioEntrada {...propsPadrao} />);

        const descricao = screen.getByLabelText("Descrição");
        await userEvent.type(descricao, "Salário");
        await userEvent.type(screen.getByLabelText("Valor (R$)"), "3000");
        await userEvent.selectOptions(screen.getByLabelText("Fonte"), "1");
        await userEvent.click(screen.getByText("Registrar Entrada"));

        expect(descricao).toHaveValue("");
        expect(screen.getByLabelText("Valor (R$)")).toHaveValue(null);
    });
});

describe("FormularioEntrada — estados", () => {
    it("desabilita o botão e exibe 'Salvando...' durante loading", () => {
        render(<FormularioEntrada {...propsPadrao} loading={true} />);
        expect(
            screen.getByRole("button", { name: "Salvando..." }),
        ).toBeDisabled();
    });

    it("exibe mensagem de sucesso quando fornecida", () => {
        render(
            <FormularioEntrada
                {...propsPadrao}
                success="Entrada registrada com sucesso!"
            />,
        );
        expect(
            screen.getByText("Entrada registrada com sucesso!"),
        ).toBeInTheDocument();
    });

    it("exibe mensagem de erro quando fornecida", () => {
        render(
            <FormularioEntrada
                {...propsPadrao}
                error="Erro ao registrar entrada."
            />,
        );
        expect(
            screen.getByText("Erro ao registrar entrada."),
        ).toBeInTheDocument();
    });
});

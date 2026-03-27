import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormularioCategoriaFonte } from "../FormularioCategoriaFonte";

/*
 * FormularioCategoriaFonte — testes de renderização, submit e estados
 * --------------------------------------------------------------------
 *
 * O FormularioCategoriaFonte é um componente controlado que serve
 * tanto para criar Categorias quanto para criar Fontes. A prop
 * `activeTab` determina qual modo está ativo: "categoria" ou "fonte".
 * O componente muda label, placeholder e texto do botão de acordo.
 *
 * Os testes são divididos em três grupos:
 *
 * 1. ABA CATEGORIA: verifica que o label "Nome da Categoria" e o
 *    botão "Criar Categoria" estão presentes, que `onSubmit` é chamado
 *    com o nome digitado pelo usuário, e que o campo é limpo após o
 *    submit — para que o usuário possa cadastrar o próximo item
 *    imediatamente sem precisar apagar o texto manualmente.
 *
 * 2. ABA FONTE: mesmos comportamentos, mas no modo "fonte" — label
 *    "Nome da Fonte", botão "Criar Fonte" e chamada ao `onSubmit`.
 *
 * 3. ESTADOS: o componente recebe `loading`, `success` e `error` como
 *    props e os reflete visualmente. Durante loading, o botão exibe
 *    "Salvando..." e fica desabilitado para evitar duplo submit.
 *    As mensagens de sucesso e erro são exibidas conforme recebidas.
 */

const propsPadrao = {
    activeTab: "categoria" as const,
    loading: false,
    success: null,
    error: null,
    onSubmit: vi.fn(),
};

describe("FormularioCategoriaFonte — aba Categoria", () => {
    it("exibe label 'Nome da Categoria'", () => {
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                activeTab="categoria"
            />,
        );
        expect(screen.getByLabelText("Nome da Categoria")).toBeInTheDocument();
    });

    it("exibe botão 'Criar Categoria'", () => {
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                activeTab="categoria"
            />,
        );
        expect(
            screen.getByRole("button", { name: "Criar Categoria" }),
        ).toBeInTheDocument();
    });

    it("chama onSubmit com o nome digitado", async () => {
        const onSubmit = vi.fn();
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                activeTab="categoria"
                onSubmit={onSubmit}
            />,
        );
        await userEvent.type(
            screen.getByLabelText("Nome da Categoria"),
            "Lazer",
        );
        await userEvent.click(
            screen.getByRole("button", { name: "Criar Categoria" }),
        );
        expect(onSubmit).toHaveBeenCalledWith("Lazer");
    });

    it("limpa o campo após submit", async () => {
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                activeTab="categoria"
            />,
        );
        const input = screen.getByLabelText("Nome da Categoria");
        await userEvent.type(input, "Lazer");
        await userEvent.click(
            screen.getByRole("button", { name: "Criar Categoria" }),
        );
        expect(input).toHaveValue("");
    });
});

describe("FormularioCategoriaFonte — aba Fonte", () => {
    it("exibe label 'Nome da Fonte'", () => {
        render(
            <FormularioCategoriaFonte {...propsPadrao} activeTab="fonte" />,
        );
        expect(screen.getByLabelText("Nome da Fonte")).toBeInTheDocument();
    });

    it("exibe botão 'Criar Fonte'", () => {
        render(
            <FormularioCategoriaFonte {...propsPadrao} activeTab="fonte" />,
        );
        expect(
            screen.getByRole("button", { name: "Criar Fonte" }),
        ).toBeInTheDocument();
    });

    it("chama onSubmit com o nome digitado", async () => {
        const onSubmit = vi.fn();
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                activeTab="fonte"
                onSubmit={onSubmit}
            />,
        );
        await userEvent.type(screen.getByLabelText("Nome da Fonte"), "Pix");
        await userEvent.click(
            screen.getByRole("button", { name: "Criar Fonte" }),
        );
        expect(onSubmit).toHaveBeenCalledWith("Pix");
    });
});

describe("FormularioCategoriaFonte — estados", () => {
    it("desabilita o botão e exibe 'Salvando...' durante loading", () => {
        render(<FormularioCategoriaFonte {...propsPadrao} loading={true} />);
        expect(
            screen.getByRole("button", { name: "Salvando..." }),
        ).toBeDisabled();
    });

    it("exibe mensagem de sucesso quando fornecida", () => {
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                success="Categoria criada com sucesso!"
            />,
        );
        expect(
            screen.getByText("Categoria criada com sucesso!"),
        ).toBeInTheDocument();
    });

    it("exibe mensagem de erro quando fornecida", () => {
        render(
            <FormularioCategoriaFonte
                {...propsPadrao}
                error="Você já possui uma categoria com este nome."
            />,
        );
        expect(
            screen.getByText("Você já possui uma categoria com este nome."),
        ).toBeInTheDocument();
    });
});

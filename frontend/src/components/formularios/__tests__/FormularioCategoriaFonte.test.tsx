import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormularioCategoriaFonte } from "../FormularioCategoriaFonte";

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

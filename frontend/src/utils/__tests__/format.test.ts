import { describe, it, expect } from "vitest";
import { formatarBRL, formatDate } from "../format";

/*
 * Utilitários de formatação — formatarBRL e formatDate
 * -----------------------------------------------------
 *
 * Este arquivo testa as duas funções de formatação usadas em toda
 * a interface para apresentar dados financeiros ao usuário brasileiro.
 *
 * formatarBRL(valor: string): string
 *   Converte uma string decimal no formato da API ("1500.00") para o
 *   formato monetário brasileiro com símbolo de real, separador de
 *   milhar (ponto) e separador decimal (vírgula): "R$ 1.500,00".
 *   Usa `Intl.NumberFormat` internamente, por isso o espaço entre
 *   "R$" e o número é um non-breaking space (\u00a0), não um espaço
 *   normal — os testes usam esse caractere explicitamente para evitar
 *   falsos positivos com espaços comuns.
 *   Valores negativos devem ser formatados como "-R$ 300,00", com o
 *   sinal antes do símbolo da moeda.
 *
 * formatDate(data: string): string
 *   Converte uma string ISO 8601 ("2026-03-19") para o formato
 *   brasileiro DD/MM/AAAA ("19/03/2026"). É usada nas tabelas de
 *   histórico e nos cards do painel para exibir datas legíveis.
 */

describe("formatarBRL", () => {
    it("formata valor positivo em reais brasileiros", () => {
        expect(formatarBRL("1500.00")).toBe("R$\u00a01.500,00");
    });

    it("formata valor negativo corretamente", () => {
        expect(formatarBRL("-300.00")).toBe("-R$\u00a0300,00");
    });

    it("formata zero corretamente", () => {
        expect(formatarBRL("0.00")).toBe("R$\u00a00,00");
    });

    it("formata valor com centavos", () => {
        expect(formatarBRL("49.99")).toBe("R$\u00a049,99");
    });

    it("formata valor grande com separador de milhar", () => {
        expect(formatarBRL("10000.00")).toBe("R$\u00a010.000,00");
    });
});

describe("formatDate", () => {
    it("formata data no padrão brasileiro DD/MM/AAAA", () => {
        expect(formatDate("2026-03-19")).toBe("19/03/2026");
    });

    it("formata data de janeiro corretamente", () => {
        expect(formatDate("2026-01-01")).toBe("01/01/2026");
    });

    it("formata data de dezembro corretamente", () => {
        expect(formatDate("2025-12-31")).toBe("31/12/2025");
    });
});

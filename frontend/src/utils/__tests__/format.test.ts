import { describe, it, expect } from "vitest";
import { formatBRL, formatDate } from "../format";

describe("formatBRL", () => {
    it("formata valor positivo em reais brasileiros", () => {
        expect(formatBRL("1500.00")).toBe("R$\u00a01.500,00");
    });

    it("formata valor negativo corretamente", () => {
        expect(formatBRL("-300.00")).toBe("-R$\u00a0300,00");
    });

    it("formata zero corretamente", () => {
        expect(formatBRL("0.00")).toBe("R$\u00a00,00");
    });

    it("formata valor com centavos", () => {
        expect(formatBRL("49.99")).toBe("R$\u00a049,99");
    });

    it("formata valor grande com separador de milhar", () => {
        expect(formatBRL("10000.00")).toBe("R$\u00a010.000,00");
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

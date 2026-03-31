import { describe, it, expect } from "vitest";
import {
    labelMes,
    ultimos3Meses,
    buildLineData,
    buildCategoriaData,
    buildFonteData,
} from "../graficos";

// ---------------------------------------------------------------------------
// labelMes
// ---------------------------------------------------------------------------

describe("labelMes", () => {
    it("converte 2026-01 em Jan/26", () => {
        expect(labelMes("2026-01")).toBe("Jan/26");
    });

    it("converte 2026-03 em Mar/26", () => {
        expect(labelMes("2026-03")).toBe("Mar/26");
    });

    it("converte 2025-12 em Dez/25", () => {
        expect(labelMes("2025-12")).toBe("Dez/25");
    });

    it("converte 2026-07 em Jul/26", () => {
        expect(labelMes("2026-07")).toBe("Jul/26");
    });

    it("converte 2026-11 em Nov/26", () => {
        expect(labelMes("2026-11")).toBe("Nov/26");
    });
});

// ---------------------------------------------------------------------------
// ultimos3Meses
// ---------------------------------------------------------------------------

describe("ultimos3Meses", () => {
    it("retorna exatamente 3 meses", () => {
        expect(ultimos3Meses()).toHaveLength(3);
    });

    it("cada item está no formato YYYY-MM", () => {
        ultimos3Meses().forEach((m) => {
            expect(m).toMatch(/^\d{4}-\d{2}$/);
        });
    });

    it("meses estão em ordem crescente", () => {
        const meses = ultimos3Meses();
        expect(meses[0] < meses[1]).toBe(true);
        expect(meses[1] < meses[2]).toBe(true);
    });

    it("o último mês é o mês atual", () => {
        const now = new Date();
        const mes = String(now.getMonth() + 1).padStart(2, "0");
        const esperado = `${String(now.getFullYear())}-${mes}`;
        expect(ultimos3Meses()[2]).toBe(esperado);
    });
});

// ---------------------------------------------------------------------------
// buildLineData
// ---------------------------------------------------------------------------

describe("buildLineData", () => {
    it("retorna 3 pontos de dados (um por mês)", () => {
        expect(buildLineData([], [])).toHaveLength(3);
    });

    it("cada ponto tem as chaves mes, Entradas e Gastos", () => {
        buildLineData([], []).forEach((p) => {
            expect(p).toHaveProperty("mes");
            expect(p).toHaveProperty("Entradas");
            expect(p).toHaveProperty("Gastos");
        });
    });

    it("retorna zeros para meses sem dados", () => {
        buildLineData([], []).forEach((p) => {
            expect(p.Gastos).toBe(0);
            expect(p.Entradas).toBe(0);
        });
    });

    it("soma gastos do mês atual corretamente", () => {
        const meses = ultimos3Meses();
        const mesAtual = meses[2];
        const gastos = [
            {
                id: 1,
                descricao: "G1",
                valor: "100.00",
                data: `${mesAtual}-01`,
                categoria: 1,
            },
            {
                id: 2,
                descricao: "G2",
                valor: "50.00",
                data: `${mesAtual}-15`,
                categoria: 1,
            },
        ];
        const result = buildLineData(gastos, []);
        expect(result[2].Gastos).toBe(150);
    });

    it("soma entradas do mês atual corretamente", () => {
        const meses = ultimos3Meses();
        const mesAtual = meses[2];
        const entradas = [
            {
                id: 1,
                descricao: "E1",
                valor: "500.00",
                data: `${mesAtual}-01`,
                fonte: 1,
            },
        ];
        const result = buildLineData([], entradas);
        expect(result[2].Entradas).toBe(500);
    });

    it("gastos do mês mais antigo não afetam o mês atual", () => {
        const meses = ultimos3Meses();
        const mesAntigo = meses[0];
        const gastos = [
            {
                id: 1,
                descricao: "G1",
                valor: "100.00",
                data: `${mesAntigo}-01`,
                categoria: 1,
            },
        ];
        const result = buildLineData(gastos, []);
        expect(result[0].Gastos).toBe(100);
        expect(result[2].Gastos).toBe(0);
    });

    it("a chave mes usa o formato Mmm/AA (ex: Mar/26)", () => {
        const result = buildLineData([], []);
        result.forEach((p) => {
            expect(p.mes).toMatch(/^[A-Z][a-z]{2}\/\d{2}$/);
        });
    });
});

// ---------------------------------------------------------------------------
// buildCategoriaData
// ---------------------------------------------------------------------------

describe("buildCategoriaData", () => {
    it("retorna lista vazia para gastos vazios", () => {
        expect(buildCategoriaData([])).toHaveLength(0);
    });

    it("agrupa gastos pela mesma categoria_nome", () => {
        const gastos = [
            {
                id: 1,
                descricao: "G1",
                valor: "100.00",
                data: "2026-01-01",
                categoria: 1,
                categoria_nome: "Alimentação",
            },
            {
                id: 2,
                descricao: "G2",
                valor: "50.00",
                data: "2026-01-02",
                categoria: 1,
                categoria_nome: "Alimentação",
            },
        ];
        const result = buildCategoriaData(gastos);
        expect(result).toHaveLength(1);
        expect(result[0].nome).toBe("Alimentação");
        expect(result[0].Total).toBe(150);
    });

    it("cria entradas separadas para categorias distintas", () => {
        const gastos = [
            {
                id: 1,
                descricao: "G1",
                valor: "100.00",
                data: "2026-01-01",
                categoria: 1,
                categoria_nome: "Alimentação",
            },
            {
                id: 2,
                descricao: "G2",
                valor: "50.00",
                data: "2026-01-02",
                categoria: 2,
                categoria_nome: "Transporte",
            },
        ];
        const result = buildCategoriaData(gastos);
        expect(result).toHaveLength(2);
    });

    it("usa 'Sem categoria' quando categoria_nome não está definido", () => {
        const gastos = [
            {
                id: 1,
                descricao: "G",
                valor: "10.00",
                data: "2026-01-01",
                categoria: 1,
            },
        ];
        const result = buildCategoriaData(gastos);
        expect(result[0].nome).toBe("Sem categoria");
    });

    it("ordena categorias por Total decrescente", () => {
        const gastos = [
            {
                id: 1,
                descricao: "G1",
                valor: "10.00",
                data: "2026-01-01",
                categoria: 1,
                categoria_nome: "Barato",
            },
            {
                id: 2,
                descricao: "G2",
                valor: "100.00",
                data: "2026-01-02",
                categoria: 2,
                categoria_nome: "Caro",
            },
        ];
        const result = buildCategoriaData(gastos);
        expect(result[0].nome).toBe("Caro");
        expect(result[1].nome).toBe("Barato");
    });

    it("Total tem no máximo 2 casas decimais", () => {
        const gastos = [
            {
                id: 1,
                descricao: "G",
                valor: "33.335",
                data: "2026-01-01",
                categoria: 1,
                categoria_nome: "Teste",
            },
        ];
        const result = buildCategoriaData(gastos);
        const decimais = result[0].Total.toString().split(".")[1] ?? "";
        expect(decimais.length).toBeLessThanOrEqual(2);
    });
});

// ---------------------------------------------------------------------------
// buildFonteData
// ---------------------------------------------------------------------------

describe("buildFonteData", () => {
    it("retorna lista vazia para entradas vazias", () => {
        expect(buildFonteData([])).toHaveLength(0);
    });

    it("agrupa entradas pela mesma fonte_nome", () => {
        const entradas = [
            {
                id: 1,
                descricao: "E1",
                valor: "500.00",
                data: "2026-01-01",
                fonte: 1,
                fonte_nome: "Salário",
            },
            {
                id: 2,
                descricao: "E2",
                valor: "200.00",
                data: "2026-01-02",
                fonte: 1,
                fonte_nome: "Salário",
            },
        ];
        const result = buildFonteData(entradas);
        expect(result).toHaveLength(1);
        expect(result[0].Total).toBe(700);
    });

    it("usa 'Sem fonte' quando fonte_nome não está definido", () => {
        const entradas = [
            {
                id: 1,
                descricao: "E",
                valor: "50.00",
                data: "2026-01-01",
                fonte: 1,
            },
        ];
        const result = buildFonteData(entradas);
        expect(result[0].nome).toBe("Sem fonte");
    });

    it("ordena fontes por Total decrescente", () => {
        const entradas = [
            {
                id: 1,
                descricao: "E1",
                valor: "10.00",
                data: "2026-01-01",
                fonte: 1,
                fonte_nome: "Pequena",
            },
            {
                id: 2,
                descricao: "E2",
                valor: "1000.00",
                data: "2026-01-02",
                fonte: 2,
                fonte_nome: "Grande",
            },
        ];
        const result = buildFonteData(entradas);
        expect(result[0].nome).toBe("Grande");
        expect(result[1].nome).toBe("Pequena");
    });

    it("cria entradas separadas para fontes distintas", () => {
        const entradas = [
            {
                id: 1,
                descricao: "E1",
                valor: "100.00",
                data: "2026-01-01",
                fonte: 1,
                fonte_nome: "Salário",
            },
            {
                id: 2,
                descricao: "E2",
                valor: "50.00",
                data: "2026-01-02",
                fonte: 2,
                fonte_nome: "Freelance",
            },
        ];
        const result = buildFonteData(entradas);
        expect(result).toHaveLength(2);
    });
});

import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../../test/server";
import {
    getCategorias,
    getFontes,
    createCategoria,
    createFonte,
    getGastos,
    getEntradas,
    getResumo,
    createGasto,
    createEntrada,
    getAllGastos,
    getAllEntradas,
} from "../financas";

// ---------------------------------------------------------------------------
// getCategorias
// ---------------------------------------------------------------------------

describe("getCategorias", () => {
    it("retorna lista de categorias", async () => {
        const { data } = await getCategorias();
        expect(data).toHaveLength(2);
        expect(data[0].nome).toBe("Alimentação");
        expect(data[1].nome).toBe("Transporte");
    });

    it("cada categoria tem id e nome", async () => {
        const { data } = await getCategorias();
        data.forEach((c) => {
            expect(c).toHaveProperty("id");
            expect(c).toHaveProperty("nome");
        });
    });
});

// ---------------------------------------------------------------------------
// getFontes
// ---------------------------------------------------------------------------

describe("getFontes", () => {
    it("retorna lista de fontes", async () => {
        const { data } = await getFontes();
        expect(data).toHaveLength(2);
        expect(data[0].nome).toBe("Nubank");
    });

    it("cada fonte tem id e nome", async () => {
        const { data } = await getFontes();
        data.forEach((f) => {
            expect(f).toHaveProperty("id");
            expect(f).toHaveProperty("nome");
        });
    });
});

// ---------------------------------------------------------------------------
// createCategoria
// ---------------------------------------------------------------------------

describe("createCategoria", () => {
    it("cria categoria e retorna o objeto criado", async () => {
        const { data } = await createCategoria("Nova Categoria");
        expect(data.id).toBe(3);
        expect(data.nome).toBe("Nova Categoria");
    });

    it("envia o nome correto no corpo da requisição", async () => {
        let corpoCapturado: { nome?: string } = {};
        server.use(
            http.post(
                "http://localhost:8000/api/financas/categorias/",
                async ({ request }) => {
                    corpoCapturado =
                        (await request.json()) as typeof corpoCapturado;
                    return HttpResponse.json(
                        { id: 10, nome: "Lazer" },
                        { status: 201 },
                    );
                },
            ),
        );
        await createCategoria("Lazer");
        expect(corpoCapturado.nome).toBe("Lazer");
    });
});

// ---------------------------------------------------------------------------
// createFonte
// ---------------------------------------------------------------------------

describe("createFonte", () => {
    it("cria fonte e retorna o objeto criado", async () => {
        const { data } = await createFonte("Nova Fonte");
        expect(data.id).toBe(3);
        expect(data.nome).toBe("Nova Fonte");
    });

    it("envia o nome correto no corpo da requisição", async () => {
        let corpoCapturado: { nome?: string } = {};
        server.use(
            http.post(
                "http://localhost:8000/api/financas/fontes/",
                async ({ request }) => {
                    corpoCapturado =
                        (await request.json()) as typeof corpoCapturado;
                    return HttpResponse.json(
                        { id: 10, nome: "Freelance" },
                        { status: 201 },
                    );
                },
            ),
        );
        await createFonte("Freelance");
        expect(corpoCapturado.nome).toBe("Freelance");
    });
});

// ---------------------------------------------------------------------------
// getGastos
// ---------------------------------------------------------------------------

describe("getGastos", () => {
    it("retorna resposta paginada de gastos", async () => {
        const { data } = await getGastos();
        expect(data.count).toBe(2);
        expect(data.results).toHaveLength(2);
        expect(data.results[0].descricao).toBe("Mercado");
    });

    it("aceita parâmetro de página", async () => {
        const { data } = await getGastos(1);
        expect(data).toHaveProperty("count");
        expect(data).toHaveProperty("results");
    });

    it("cada gasto tem os campos obrigatórios", async () => {
        const { data } = await getGastos();
        data.results.forEach((g) => {
            expect(g).toHaveProperty("id");
            expect(g).toHaveProperty("descricao");
            expect(g).toHaveProperty("valor");
            expect(g).toHaveProperty("data");
            expect(g).toHaveProperty("categoria");
        });
    });
});

// ---------------------------------------------------------------------------
// getEntradas
// ---------------------------------------------------------------------------

describe("getEntradas", () => {
    it("retorna resposta paginada de entradas", async () => {
        const { data } = await getEntradas();
        expect(data.count).toBe(1);
        expect(data.results).toHaveLength(1);
        expect(data.results[0].descricao).toBe("Salário");
    });

    it("cada entrada tem os campos obrigatórios", async () => {
        const { data } = await getEntradas();
        data.results.forEach((e) => {
            expect(e).toHaveProperty("id");
            expect(e).toHaveProperty("descricao");
            expect(e).toHaveProperty("valor");
            expect(e).toHaveProperty("data");
            expect(e).toHaveProperty("fonte");
        });
    });
});

// ---------------------------------------------------------------------------
// getResumo
// ---------------------------------------------------------------------------

describe("getResumo", () => {
    it("retorna resumo financeiro com os três totais", async () => {
        const { data } = await getResumo();
        expect(data.total_entradas).toBe("1500.00");
        expect(data.total_gastos).toBe("800.00");
        expect(data.saldo).toBe("700.00");
    });
});

// ---------------------------------------------------------------------------
// createGasto
// ---------------------------------------------------------------------------

describe("createGasto", () => {
    it("cria gasto e retorna o objeto criado", async () => {
        const payload = {
            descricao: "Mercado",
            valor: "50.00",
            data: "2026-03-19",
            categoria: 1,
        };
        const { data } = await createGasto(payload);
        expect(data.id).toBe(1);
        expect(data.descricao).toBe("Mercado");
    });
});

// ---------------------------------------------------------------------------
// createEntrada
// ---------------------------------------------------------------------------

describe("createEntrada", () => {
    it("cria entrada e retorna o objeto criado", async () => {
        const payload = {
            descricao: "Salário",
            valor: "3000.00",
            data: "2026-03-19",
            fonte: 1,
        };
        const { data } = await createEntrada(payload);
        expect(data.id).toBe(1);
        expect(data.descricao).toBe("Salário");
    });
});

// ---------------------------------------------------------------------------
// getAllGastos — paginação automática
// ---------------------------------------------------------------------------

describe("getAllGastos", () => {
    it("retorna todos os gastos de uma única página", async () => {
        const todos = await getAllGastos();
        expect(todos).toHaveLength(2);
    });

    it("pagina e coleta gastos de múltiplas páginas", async () => {
        server.use(
            http.get(
                "http://localhost:8000/api/financas/gastos/",
                ({ request }) => {
                    const url = new URL(request.url);
                    const pagina = url.searchParams.get("page") ?? "1";
                    if (pagina === "1") {
                        return HttpResponse.json({
                            count: 2,
                            next: "http://localhost:8000/api/financas/gastos/?page=2",
                            previous: null,
                            results: [
                                {
                                    id: 1,
                                    descricao: "G1",
                                    valor: "10.00",
                                    data: "2026-01-01",
                                    categoria: 1,
                                },
                            ],
                        });
                    }
                    return HttpResponse.json({
                        count: 2,
                        next: null,
                        previous: "...",
                        results: [
                            {
                                id: 2,
                                descricao: "G2",
                                valor: "20.00",
                                data: "2026-01-02",
                                categoria: 1,
                            },
                        ],
                    });
                },
            ),
        );
        const todos = await getAllGastos();
        expect(todos).toHaveLength(2);
        expect(todos[0].descricao).toBe("G1");
        expect(todos[1].descricao).toBe("G2");
    });

    it("para de paginar quando next é null", async () => {
        let chamadas = 0;
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () => {
                chamadas++;
                return HttpResponse.json({
                    count: 1,
                    next: null,
                    previous: null,
                    results: [
                        {
                            id: 1,
                            descricao: "G",
                            valor: "10.00",
                            data: "2026-01-01",
                            categoria: 1,
                        },
                    ],
                });
            }),
        );
        await getAllGastos();
        expect(chamadas).toBe(1);
    });
});

// ---------------------------------------------------------------------------
// getAllEntradas — paginação automática
// ---------------------------------------------------------------------------

describe("getAllEntradas", () => {
    it("retorna todas as entradas de uma única página", async () => {
        const todas = await getAllEntradas();
        expect(todas).toHaveLength(1);
    });

    it("pagina e coleta entradas de múltiplas páginas", async () => {
        server.use(
            http.get(
                "http://localhost:8000/api/financas/entradas/",
                ({ request }) => {
                    const url = new URL(request.url);
                    const pagina = url.searchParams.get("page") ?? "1";
                    if (pagina === "1") {
                        return HttpResponse.json({
                            count: 2,
                            next: "http://localhost:8000/api/financas/entradas/?page=2",
                            previous: null,
                            results: [
                                {
                                    id: 1,
                                    descricao: "E1",
                                    valor: "100.00",
                                    data: "2026-01-01",
                                    fonte: 1,
                                },
                            ],
                        });
                    }
                    return HttpResponse.json({
                        count: 2,
                        next: null,
                        previous: "...",
                        results: [
                            {
                                id: 2,
                                descricao: "E2",
                                valor: "200.00",
                                data: "2026-01-02",
                                fonte: 1,
                            },
                        ],
                    });
                },
            ),
        );
        const todas = await getAllEntradas();
        expect(todas).toHaveLength(2);
        expect(todas[0].descricao).toBe("E1");
        expect(todas[1].descricao).toBe("E2");
    });
});

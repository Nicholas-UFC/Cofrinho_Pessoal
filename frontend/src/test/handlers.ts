import { http, HttpResponse } from "msw";

const BASE = "http://localhost:8000";

// Token JWT mínimo válido com exp no futuro (1 hora)
export function makeFakeToken(isStaff = false): string {
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const exp = Math.floor(Date.now() / 1000) + 3600;
    const payload = btoa(
        JSON.stringify({ username: "testuser", is_staff: isStaff, exp }),
    );
    return `${header}.${payload}.fakesig`;
}

export function makeExpiredToken(): string {
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const exp = Math.floor(Date.now() / 1000) - 1;
    const payload = btoa(
        JSON.stringify({ username: "testuser", is_staff: false, exp }),
    );
    return `${header}.${payload}.fakesig`;
}

export const handlers = [
    // Login retorna info do usuário; tokens são definidos via cookie httpOnly.
    http.post(`${BASE}/api/token/`, () =>
        HttpResponse.json({ username: "testuser", is_staff: false }),
    ),

    // Refresh define novo cookie; corpo apenas indica sucesso.
    http.post(`${BASE}/api/token/refresh/`, () =>
        HttpResponse.json({ status: "ok" }),
    ),

    // Logout blacklista o refresh token e limpa cookies.
    http.post(`${BASE}/api/token/logout/`, () =>
        HttpResponse.json({ status: "logout realizado com sucesso." }),
    ),

    http.get(`${BASE}/api/financas/resumo/`, () =>
        HttpResponse.json({
            total_entradas: "1500.00",
            total_gastos: "800.00",
            saldo: "700.00",
        }),
    ),

    http.get(`${BASE}/api/financas/categorias/`, () =>
        HttpResponse.json([
            { id: 1, nome: "Alimentação" },
            { id: 2, nome: "Transporte" },
        ]),
    ),

    http.get(`${BASE}/api/financas/fontes/`, () =>
        HttpResponse.json([
            { id: 1, nome: "Nubank" },
            { id: 2, nome: "Salário" },
        ]),
    ),

    http.post(`${BASE}/api/financas/categorias/`, () =>
        HttpResponse.json({ id: 3, nome: "Nova Categoria" }, { status: 201 }),
    ),

    http.post(`${BASE}/api/financas/fontes/`, () =>
        HttpResponse.json({ id: 3, nome: "Nova Fonte" }, { status: 201 }),
    ),

    http.post(`${BASE}/api/financas/gastos/`, () =>
        HttpResponse.json(
            {
                id: 1,
                descricao: "Mercado",
                valor: "50.00",
                data: "2026-03-19",
                categoria: 1,
            },
            { status: 201 },
        ),
    ),

    http.post(`${BASE}/api/financas/entradas/`, () =>
        HttpResponse.json(
            {
                id: 1,
                descricao: "Salário",
                valor: "3000.00",
                data: "2026-03-19",
                fonte: 1,
            },
            { status: 201 },
        ),
    ),

    http.get(`${BASE}/api/financas/gastos/`, () =>
        HttpResponse.json({
            count: 2,
            next: null,
            previous: null,
            results: [
                {
                    id: 1,
                    descricao: "Mercado",
                    valor: "50.00",
                    data: "2026-03-01",
                    categoria: 1,
                    categoria_nome: "Alimentação",
                },
                {
                    id: 2,
                    descricao: "Uber",
                    valor: "25.00",
                    data: "2026-03-02",
                    categoria: 2,
                    categoria_nome: "Transporte",
                },
            ],
        }),
    ),

    http.get(`${BASE}/api/financas/entradas/`, () =>
        HttpResponse.json({
            count: 1,
            next: null,
            previous: null,
            results: [
                {
                    id: 1,
                    descricao: "Salário",
                    valor: "3000.00",
                    data: "2026-03-05",
                    fonte: 1,
                    fonte_nome: "Nubank",
                },
            ],
        }),
    ),
];

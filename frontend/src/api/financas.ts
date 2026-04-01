import api from "./cliente";

export interface Categoria {
    id: number;
    nome: string;
}

export interface Fonte {
    id: number;
    nome: string;
}

export interface Gasto {
    id: number;
    descricao: string;
    valor: string;
    data: string;
    categoria: number;
    categoria_nome?: string;
}

export interface Entrada {
    id: number;
    descricao: string;
    valor: string;
    data: string;
    fonte: number;
    fonte_nome?: string;
}

export interface Resumo {
    total_entradas: string;
    total_gastos: string;
    saldo: string;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export const getCategorias = (): Promise<{ data: Categoria[] }> =>
    api.get("/api/financas/categorias/") as Promise<{ data: Categoria[] }>;

export const createCategoria = (nome: string): Promise<{ data: Categoria }> =>
    api.post("/api/financas/categorias/", { nome }) as Promise<{
        data: Categoria;
    }>;

export const getFontes = (): Promise<{ data: Fonte[] }> =>
    api.get("/api/financas/fontes/") as Promise<{ data: Fonte[] }>;

export const createFonte = (nome: string): Promise<{ data: Fonte }> =>
    api.post("/api/financas/fontes/", { nome }) as Promise<{ data: Fonte }>;

export const getGastos = (
    page = 1,
): Promise<{ data: PaginatedResponse<Gasto> }> =>
    api.get(`/api/financas/gastos/?page=${String(page)}`) as Promise<{
        data: PaginatedResponse<Gasto>;
    }>;

export const createGasto = (
    payload: Omit<Gasto, "id" | "categoria_nome">,
): Promise<{ data: Gasto }> =>
    api.post("/api/financas/gastos/", payload) as Promise<{ data: Gasto }>;

export const getEntradas = (
    page = 1,
): Promise<{ data: PaginatedResponse<Entrada> }> =>
    api.get(`/api/financas/entradas/?page=${String(page)}`) as Promise<{
        data: PaginatedResponse<Entrada>;
    }>;

export const createEntrada = (
    payload: Omit<Entrada, "id" | "fonte_nome">,
): Promise<{ data: Entrada }> =>
    api.post("/api/financas/entradas/", payload) as Promise<{ data: Entrada }>;

export const getResumo = (): Promise<{ data: Resumo }> =>
    api.get("/api/financas/resumo/") as Promise<{ data: Resumo }>;

export async function getAllGastos(): Promise<Gasto[]> {
    const all: Gasto[] = [];
    let page = 1;
    let hasNext = true;
    while (hasNext) {
        const { data } = await getGastos(page);
        all.push(...data.results);
        hasNext = data.next !== null;
        page++;
    }
    return all;
}

export async function getAllEntradas(): Promise<Entrada[]> {
    const all: Entrada[] = [];
    let page = 1;
    let hasNext = true;
    while (hasNext) {
        const { data } = await getEntradas(page);
        all.push(...data.results);
        hasNext = data.next !== null;
        page++;
    }
    return all;
}

import api from "./axios";

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
    api.get<Categoria[]>("/api/financas/categorias/");

export const createCategoria = (nome: string): Promise<{ data: Categoria }> =>
    api.post<Categoria>("/api/financas/categorias/", { nome });

export const getFontes = (): Promise<{ data: Fonte[] }> =>
    api.get<Fonte[]>("/api/financas/fontes/");

export const createFonte = (nome: string): Promise<{ data: Fonte }> =>
    api.post<Fonte>("/api/financas/fontes/", { nome });

export const getGastos = (
    page = 1,
): Promise<{ data: PaginatedResponse<Gasto> }> =>
    api.get<PaginatedResponse<Gasto>>(
        `/api/financas/gastos/?page=${String(page)}`,
    );

export const createGasto = (
    payload: Omit<Gasto, "id" | "categoria_nome">,
): Promise<{ data: Gasto }> =>
    api.post<Gasto>("/api/financas/gastos/", payload);

export const getEntradas = (
    page = 1,
): Promise<{ data: PaginatedResponse<Entrada> }> =>
    api.get<PaginatedResponse<Entrada>>(
        `/api/financas/entradas/?page=${String(page)}`,
    );

export const createEntrada = (
    payload: Omit<Entrada, "id" | "fonte_nome">,
): Promise<{ data: Entrada }> =>
    api.post<Entrada>("/api/financas/entradas/", payload);

export const getResumo = (): Promise<{ data: Resumo }> =>
    api.get<Resumo>("/api/financas/resumo/");

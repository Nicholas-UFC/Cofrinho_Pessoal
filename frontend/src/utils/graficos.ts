import { type Gasto, type Entrada } from "../api/financas";

export interface MonthPoint {
    mes: string;
    Entradas: number;
    Gastos: number;
}

export interface CategoriaPoint {
    nome: string;
    Total: number;
}

export function labelMes(iso: string): string {
    const [year, month] = iso.split("-");
    const nomes = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ];
    return `${nomes[Number(month) - 1]}/${year.slice(2)}`;
}

export function ultimos3Meses(): string[] {
    const meses: string[] = [];
    const now = new Date();
    for (let i = 2; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const m = String(d.getMonth() + 1).padStart(2, "0");
        meses.push(`${String(d.getFullYear())}-${m}`);
    }
    return meses;
}

export function buildLineData(
    gastos: Gasto[],
    entradas: Entrada[],
): MonthPoint[] {
    const meses = ultimos3Meses();
    return meses.map((mes) => {
        const totalGastos = gastos
            .filter((g) => g.data.startsWith(mes))
            .reduce((acc, g) => acc + Number(g.valor), 0);
        const totalEntradas = entradas
            .filter((e) => e.data.startsWith(mes))
            .reduce((acc, e) => acc + Number(e.valor), 0);
        return {
            mes: labelMes(mes),
            Entradas: Number(totalEntradas.toFixed(2)),
            Gastos: Number(totalGastos.toFixed(2)),
        };
    });
}

export function buildCategoriaData(gastos: Gasto[]): CategoriaPoint[] {
    const map = new Map<string, number>();
    gastos.forEach((g) => {
        const cat = g.categoria_nome ?? "Sem categoria";
        map.set(cat, (map.get(cat) ?? 0) + Number(g.valor));
    });
    return Array.from(map.entries())
        .map(([nome, total]) => ({ nome, Total: Number(total.toFixed(2)) }))
        .sort((a, b) => b.Total - a.Total);
}

export function buildFonteData(entradas: Entrada[]): CategoriaPoint[] {
    const map = new Map<string, number>();
    entradas.forEach((e) => {
        const fonte = e.fonte_nome ?? "Sem fonte";
        map.set(fonte, (map.get(fonte) ?? 0) + Number(e.valor));
    });
    return Array.from(map.entries())
        .map(([nome, total]) => ({ nome, Total: Number(total.toFixed(2)) }))
        .sort((a, b) => b.Total - a.Total);
}

export function formatBRL(value: string): string {
    return Number(value).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}

export function formatDate(dateStr: string): string {
    return new Date(dateStr + "T00:00:00").toLocaleDateString("pt-BR");
}

import { useState, type JSX } from "react";
import { type Gasto, type Entrada } from "../api/financas";
import { formatarBRL, formatDate } from "../utils/format";
import { useHistorico } from "../hooks/useHistorico";

type View = "gastos" | "entradas";

export default function PaginaHistorico(): JSX.Element {
    const [view, setView] = useState<View>("gastos");
    const {
        gastos,
        entradas,
        loading,
        error,
        gastoPage,
        entradaPage,
        setGastoPage,
        setEntradaPage,
    } = useHistorico(view);

    const currentPage = view === "gastos" ? gastoPage : entradaPage;
    const setPage = view === "gastos" ? setGastoPage : setEntradaPage;
    const data = view === "gastos" ? gastos : entradas;

    return (
        <div>
            <h1
                style={{ color: "#f1f5f9" }}
                className="text-2xl font-bold mb-6"
            >
                Histórico
            </h1>

            <div className="flex gap-2 mb-6">
                {(["gastos", "entradas"] as View[]).map((v) => (
                    <button
                        key={v}
                        onClick={() => {
                            setView(v);
                        }}
                        style={{
                            backgroundColor:
                                view === v ? "#22c55e" : "#16213e",
                            color: view === v ? "#0f3460" : "#f1f5f9",
                            border: "1px solid #1e3a5f",
                        }}
                        className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        {v === "gastos" ? "📉 Gastos" : "📈 Entradas"}
                    </button>
                ))}
            </div>

            {loading && (
                <p style={{ color: "#94a3b8" }} className="text-sm">
                    Carregando...
                </p>
            )}
            {error && <p className="text-red-400 text-sm">{error}</p>}

            {!loading && !error && data && (
                <>
                    <div
                        style={{
                            backgroundColor: "#16213e",
                            border: "1px solid #1e3a5f",
                        }}
                        className="rounded-xl shadow overflow-hidden"
                    >
                        <table className="w-full text-sm">
                            <thead>
                                <tr
                                    style={{
                                        backgroundColor: "#0f3460",
                                        color: "#94a3b8",
                                    }}
                                >
                                    <th className="text-left px-4 py-3 font-medium">
                                        Descrição
                                    </th>
                                    <th className="text-left px-4 py-3 font-medium">
                                        {view === "gastos"
                                            ? "Categoria"
                                            : "Fonte"}
                                    </th>
                                    <th className="text-left px-4 py-3 font-medium">
                                        Data
                                    </th>
                                    <th className="text-right px-4 py-3 font-medium">
                                        Valor
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.results.length === 0 && (
                                    <tr>
                                        <td
                                            colSpan={4}
                                            style={{ color: "#94a3b8" }}
                                            className="text-center py-8"
                                        >
                                            Nenhum registro encontrado.
                                        </td>
                                    </tr>
                                )}
                                {view === "gastos" &&
                                    (data.results as Gasto[]).map((g) => (
                                        <tr
                                            key={g.id}
                                            style={{
                                                borderTop: "1px solid #1e3a5f",
                                                color: "#f1f5f9",
                                            }}
                                        >
                                            <td className="px-4 py-3">
                                                {g.descricao}
                                            </td>
                                            <td
                                                style={{ color: "#94a3b8" }}
                                                className="px-4 py-3"
                                            >
                                                {g.categoria_nome ?? "—"}
                                            </td>
                                            <td
                                                style={{ color: "#94a3b8" }}
                                                className="px-4 py-3"
                                            >
                                                {formatDate(g.data)}
                                            </td>
                                            <td className="px-4 py-3 text-right text-red-400 font-medium">
                                                {formatarBRL(g.valor)}
                                            </td>
                                        </tr>
                                    ))}
                                {view === "entradas" &&
                                    (data.results as Entrada[]).map((e) => (
                                        <tr
                                            key={e.id}
                                            style={{
                                                borderTop: "1px solid #1e3a5f",
                                                color: "#f1f5f9",
                                            }}
                                        >
                                            <td className="px-4 py-3">
                                                {e.descricao}
                                            </td>
                                            <td
                                                style={{ color: "#94a3b8" }}
                                                className="px-4 py-3"
                                            >
                                                {e.fonte_nome ?? "—"}
                                            </td>
                                            <td
                                                style={{ color: "#94a3b8" }}
                                                className="px-4 py-3"
                                            >
                                                {formatDate(e.data)}
                                            </td>
                                            <td
                                                style={{ color: "#22c55e" }}
                                                className="px-4 py-3 text-right font-medium"
                                            >
                                                {formatarBRL(e.valor)}
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="flex items-center justify-between mt-4">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => {
                                setPage((p) => p - 1);
                            }}
                            style={{
                                backgroundColor: "#16213e",
                                border: "1px solid #1e3a5f",
                                color: "#f1f5f9",
                            }}
                            className="px-4 py-2 rounded-lg text-sm disabled:opacity-40"
                        >
                            ← Anterior
                        </button>
                        <span style={{ color: "#94a3b8" }} className="text-sm">
                            Página {currentPage} · {data.count}{" "}
                            {data.count === 1 ? "registro" : "registros"}
                        </span>
                        <button
                            disabled={!data.next}
                            onClick={() => {
                                setPage((p) => p + 1);
                            }}
                            style={{
                                backgroundColor: "#16213e",
                                border: "1px solid #1e3a5f",
                                color: "#f1f5f9",
                            }}
                            className="px-4 py-2 rounded-lg text-sm disabled:opacity-40"
                        >
                            Próxima →
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}

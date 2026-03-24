import {
    useEffect,
    useState,
    type Dispatch,
    type SetStateAction,
} from "react";
import {
    getGastos,
    getEntradas,
    type Gasto,
    type Entrada,
    type PaginatedResponse,
} from "../api/financas";

type View = "gastos" | "entradas";

interface EstadoHistorico {
    gastos: PaginatedResponse<Gasto> | null;
    entradas: PaginatedResponse<Entrada> | null;
    loading: boolean;
    error: string | null;
    gastoPage: number;
    entradaPage: number;
    setGastoPage: Dispatch<SetStateAction<number>>;
    setEntradaPage: Dispatch<SetStateAction<number>>;
}

export function useHistorico(view: View): EstadoHistorico {
    const [gastos, setGastos] = useState<PaginatedResponse<Gasto> | null>(
        null,
    );
    const [entradas, setEntradas] =
        useState<PaginatedResponse<Entrada> | null>(null);
    const [gastoPage, setGastoPage] = useState(1);
    const [entradaPage, setEntradaPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;

        async function buscarDados(): Promise<void> {
            setLoading(true);
            setError(null);
            try {
                if (view === "gastos") {
                    const { data } = await getGastos(gastoPage);
                    if (!cancelled) setGastos(data);
                } else {
                    const { data } = await getEntradas(entradaPage);
                    if (!cancelled) setEntradas(data);
                }
            } catch {
                if (!cancelled) setError("Erro ao carregar histórico.");
            } finally {
                if (!cancelled) setLoading(false);
            }
        }

        void buscarDados();
        return () => {
            cancelled = true;
        };
    }, [view, gastoPage, entradaPage]);

    return {
        gastos,
        entradas,
        loading,
        error,
        gastoPage,
        entradaPage,
        setGastoPage,
        setEntradaPage,
    };
}

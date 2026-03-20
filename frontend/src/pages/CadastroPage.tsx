import { useState, useEffect, type JSX } from "react";
import {
    getCategorias,
    getFontes,
    createGasto,
    createEntrada,
    createCategoria,
    createFonte,
    type Categoria,
    type Fonte,
} from "../api/financas";

type Tab = "gasto" | "entrada" | "categoria" | "fonte";

const TABS: { id: Tab; label: string; icon: string }[] = [
    { id: "gasto", label: "Gasto", icon: "📉" },
    { id: "entrada", label: "Entrada", icon: "📈" },
    { id: "categoria", label: "Categoria", icon: "🏷️" },
    { id: "fonte", label: "Fonte", icon: "🏦" },
];

function SuccessMessage({ message }: { message: string }): JSX.Element {
    return (
        <p style={{ color: "#22c55e" }} className="text-sm text-center mt-2">
            {message}
        </p>
    );
}

function ErrorMessage({ message }: { message: string }): JSX.Element {
    return <p className="text-red-400 text-sm text-center mt-2">{message}</p>;
}

function inputStyle(): React.CSSProperties {
    return {
        backgroundColor: "#0f3460",
        border: "1px solid #1e3a5f",
        color: "#f1f5f9",
    };
}

function labelStyle(): React.CSSProperties {
    return { color: "#94a3b8" };
}

const INPUT_CLASS =
    "rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-green-500 w-full";

export default function CadastroPage(): JSX.Element {
    const [activeTab, setActiveTab] = useState<Tab>("gasto");
    const [categorias, setCategorias] = useState<Categoria[]>([]);
    const [fontes, setFontes] = useState<Fonte[]>([]);
    const [success, setSuccess] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const [gastoDescricao, setGastoDescricao] = useState("");
    const [gastoValor, setGastoValor] = useState("");
    const [gastoData, setGastoData] = useState(
        new Date().toISOString().slice(0, 10),
    );
    const [gastoCategoria, setGastoCategoria] = useState("");

    const [entradaDescricao, setEntradaDescricao] = useState("");
    const [entradaValor, setEntradaValor] = useState("");
    const [entradaData, setEntradaData] = useState(
        new Date().toISOString().slice(0, 10),
    );
    const [entradaFonte, setEntradaFonte] = useState("");

    const [nomeSimples, setNomeSimples] = useState("");

    useEffect(() => {
        void getCategorias().then(({ data }) => {
            setCategorias(data);
        });
        void getFontes().then(({ data }) => {
            setFontes(data);
        });
    }, []);

    function reset(): void {
        setSuccess(null);
        setError(null);
    }

    function handleApiError(err: unknown): void {
        const data =
            err instanceof Object && "response" in err
                ? (
                      err as {
                          response?: { data?: Record<string, string[]> };
                      }
                  ).response?.data
                : undefined;
        const first = data ? Object.values(data)[0]?.[0] : null;
        setError(first ?? "Erro ao salvar. Tente novamente.");
        setLoading(false);
    }

    async function handleGasto(e: React.SyntheticEvent): Promise<void> {
        e.preventDefault();
        reset();
        setLoading(true);
        try {
            await createGasto({
                descricao: gastoDescricao,
                valor: gastoValor,
                data: gastoData,
                categoria: Number(gastoCategoria),
            });
            setGastoDescricao("");
            setGastoValor("");
            setSuccess("Gasto registrado com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleEntrada(e: React.SyntheticEvent): Promise<void> {
        e.preventDefault();
        reset();
        setLoading(true);
        try {
            await createEntrada({
                descricao: entradaDescricao,
                valor: entradaValor,
                data: entradaData,
                fonte: Number(entradaFonte),
            });
            setEntradaDescricao("");
            setEntradaValor("");
            setSuccess("Entrada registrada com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleCategoria(e: React.SyntheticEvent): Promise<void> {
        e.preventDefault();
        reset();
        setLoading(true);
        try {
            const { data } = await createCategoria(nomeSimples);
            setCategorias((prev) => [...prev, data]);
            setNomeSimples("");
            setSuccess("Categoria criada com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleFonte(e: React.SyntheticEvent): Promise<void> {
        e.preventDefault();
        reset();
        setLoading(true);
        try {
            const { data } = await createFonte(nomeSimples);
            setFontes((prev) => [...prev, data]);
            setNomeSimples("");
            setSuccess("Fonte criada com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <h1
                style={{ color: "#f1f5f9" }}
                className="text-2xl font-bold mb-6"
            >
                Cadastro
            </h1>

            <div className="flex gap-2 mb-6">
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => {
                            setActiveTab(tab.id);
                            reset();
                            setNomeSimples("");
                        }}
                        style={{
                            backgroundColor:
                                activeTab === tab.id ? "#22c55e" : "#16213e",
                            color:
                                activeTab === tab.id ? "#0f3460" : "#f1f5f9",
                            border: "1px solid #1e3a5f",
                        }}
                        className="px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                    >
                        <span>{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </div>

            <div
                style={{
                    backgroundColor: "#16213e",
                    border: "1px solid #1e3a5f",
                }}
                className="rounded-xl p-6 shadow max-w-lg"
            >
                {activeTab === "gasto" && (
                    <form
                        onSubmit={(e) => {
                            void handleGasto(e);
                        }}
                        className="flex flex-col gap-4"
                    >
                        <div className="flex flex-col gap-1">
                            <label
                                htmlFor="gasto-descricao"
                                style={labelStyle()}
                                className="text-sm"
                            >
                                Descrição
                            </label>
                            <input
                                id="gasto-descricao"
                                style={inputStyle()}
                                className={INPUT_CLASS}
                                value={gastoDescricao}
                                onChange={(e) => {
                                    setGastoDescricao(e.target.value);
                                }}
                                required
                                placeholder="Ex: Mercado"
                            />
                        </div>
                        <div className="flex gap-3">
                            <div className="flex flex-col gap-1 flex-1">
                                <label
                                    htmlFor="gasto-valor"
                                    style={labelStyle()}
                                    className="text-sm"
                                >
                                    Valor (R$)
                                </label>
                                <input
                                    id="gasto-valor"
                                    style={inputStyle()}
                                    className={INPUT_CLASS}
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    value={gastoValor}
                                    onChange={(e) => {
                                        setGastoValor(e.target.value);
                                    }}
                                    required
                                    placeholder="0,00"
                                />
                            </div>
                            <div className="flex flex-col gap-1 flex-1">
                                <label
                                    htmlFor="gasto-data"
                                    style={labelStyle()}
                                    className="text-sm"
                                >
                                    Data
                                </label>
                                <input
                                    id="gasto-data"
                                    style={inputStyle()}
                                    className={INPUT_CLASS}
                                    type="date"
                                    value={gastoData}
                                    onChange={(e) => {
                                        setGastoData(e.target.value);
                                    }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="flex flex-col gap-1">
                            <label
                                htmlFor="gasto-categoria"
                                style={labelStyle()}
                                className="text-sm"
                            >
                                Categoria
                            </label>
                            <select
                                id="gasto-categoria"
                                style={inputStyle()}
                                className={INPUT_CLASS}
                                value={gastoCategoria}
                                onChange={(e) => {
                                    setGastoCategoria(e.target.value);
                                }}
                                required
                            >
                                <option value="">Selecione...</option>
                                {categorias.map((c) => (
                                    <option key={c.id} value={c.id}>
                                        {c.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        {success && <SuccessMessage message={success} />}
                        {error && <ErrorMessage message={error} />}
                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                backgroundColor: "#22c55e",
                                color: "#0f3460",
                            }}
                            className="rounded-lg py-2 font-semibold text-sm hover:opacity-80 disabled:opacity-50 transition-opacity"
                        >
                            {loading ? "Salvando..." : "Registrar Gasto"}
                        </button>
                    </form>
                )}

                {activeTab === "entrada" && (
                    <form
                        onSubmit={(e) => {
                            void handleEntrada(e);
                        }}
                        className="flex flex-col gap-4"
                    >
                        <div className="flex flex-col gap-1">
                            <label
                                htmlFor="entrada-descricao"
                                style={labelStyle()}
                                className="text-sm"
                            >
                                Descrição
                            </label>
                            <input
                                id="entrada-descricao"
                                style={inputStyle()}
                                className={INPUT_CLASS}
                                value={entradaDescricao}
                                onChange={(e) => {
                                    setEntradaDescricao(e.target.value);
                                }}
                                required
                                placeholder="Ex: Salário"
                            />
                        </div>
                        <div className="flex gap-3">
                            <div className="flex flex-col gap-1 flex-1">
                                <label
                                    htmlFor="entrada-valor"
                                    style={labelStyle()}
                                    className="text-sm"
                                >
                                    Valor (R$)
                                </label>
                                <input
                                    id="entrada-valor"
                                    style={inputStyle()}
                                    className={INPUT_CLASS}
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    value={entradaValor}
                                    onChange={(e) => {
                                        setEntradaValor(e.target.value);
                                    }}
                                    required
                                    placeholder="0,00"
                                />
                            </div>
                            <div className="flex flex-col gap-1 flex-1">
                                <label
                                    htmlFor="entrada-data"
                                    style={labelStyle()}
                                    className="text-sm"
                                >
                                    Data
                                </label>
                                <input
                                    id="entrada-data"
                                    style={inputStyle()}
                                    className={INPUT_CLASS}
                                    type="date"
                                    value={entradaData}
                                    onChange={(e) => {
                                        setEntradaData(e.target.value);
                                    }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="flex flex-col gap-1">
                            <label
                                htmlFor="entrada-fonte"
                                style={labelStyle()}
                                className="text-sm"
                            >
                                Fonte
                            </label>
                            <select
                                id="entrada-fonte"
                                style={inputStyle()}
                                className={INPUT_CLASS}
                                value={entradaFonte}
                                onChange={(e) => {
                                    setEntradaFonte(e.target.value);
                                }}
                                required
                            >
                                <option value="">Selecione...</option>
                                {fontes.map((f) => (
                                    <option key={f.id} value={f.id}>
                                        {f.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        {success && <SuccessMessage message={success} />}
                        {error && <ErrorMessage message={error} />}
                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                backgroundColor: "#22c55e",
                                color: "#0f3460",
                            }}
                            className="rounded-lg py-2 font-semibold text-sm hover:opacity-80 disabled:opacity-50 transition-opacity"
                        >
                            {loading ? "Salvando..." : "Registrar Entrada"}
                        </button>
                    </form>
                )}

                {(activeTab === "categoria" || activeTab === "fonte") && (
                    <form
                        onSubmit={(e) => {
                            void (activeTab === "categoria"
                                ? handleCategoria(e)
                                : handleFonte(e));
                        }}
                        className="flex flex-col gap-4"
                    >
                        <div className="flex flex-col gap-1">
                            <label
                                htmlFor="nome-simples"
                                style={labelStyle()}
                                className="text-sm"
                            >
                                Nome da{" "}
                                {activeTab === "categoria"
                                    ? "Categoria"
                                    : "Fonte"}
                            </label>
                            <input
                                id="nome-simples"
                                style={inputStyle()}
                                className={INPUT_CLASS}
                                value={nomeSimples}
                                onChange={(e) => {
                                    setNomeSimples(e.target.value);
                                }}
                                required
                                placeholder={
                                    activeTab === "categoria"
                                        ? "Ex: Alimentação"
                                        : "Ex: Nubank"
                                }
                            />
                        </div>
                        {success && <SuccessMessage message={success} />}
                        {error && <ErrorMessage message={error} />}
                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                backgroundColor: "#22c55e",
                                color: "#0f3460",
                            }}
                            className="rounded-lg py-2 font-semibold text-sm hover:opacity-80 disabled:opacity-50 transition-opacity"
                        >
                            {loading
                                ? "Salvando..."
                                : `Criar ${activeTab === "categoria" ? "Categoria" : "Fonte"}`}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}

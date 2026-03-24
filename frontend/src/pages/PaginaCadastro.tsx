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
import { FormularioGasto } from "../components/formularios/FormularioGasto";
import { FormularioEntrada } from "../components/formularios/FormularioEntrada";
import { FormularioCategoriaFonte } from "../components/formularios/FormularioCategoriaFonte";

type Tab = "gasto" | "entrada" | "categoria" | "fonte";

const TABS: { id: Tab; label: string; icon: string }[] = [
    { id: "gasto", label: "Gasto", icon: "📉" },
    { id: "entrada", label: "Entrada", icon: "📈" },
    { id: "categoria", label: "Categoria", icon: "🏷️" },
    { id: "fonte", label: "Fonte", icon: "🏦" },
];

export default function PaginaCadastro(): JSX.Element {
    const [activeTab, setActiveTab] = useState<Tab>("gasto");
    const [categorias, setCategorias] = useState<Categoria[]>([]);
    const [fontes, setFontes] = useState<Fonte[]>([]);
    const [success, setSuccess] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

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

    async function handleGasto(
        descricao: string,
        valor: string,
        data: string,
        categoria: string,
    ): Promise<void> {
        reset();
        setLoading(true);
        try {
            await createGasto({
                descricao,
                valor,
                data,
                categoria: Number(categoria),
            });
            setSuccess("Gasto registrado com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleEntrada(
        descricao: string,
        valor: string,
        data: string,
        fonte: string,
    ): Promise<void> {
        reset();
        setLoading(true);
        try {
            await createEntrada({
                descricao,
                valor,
                data,
                fonte: Number(fonte),
            });
            setSuccess("Entrada registrada com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleCategoria(nome: string): Promise<void> {
        reset();
        setLoading(true);
        try {
            const { data } = await createCategoria(nome);
            setCategorias((prev) => [...prev, data]);
            setSuccess("Categoria criada com sucesso!");
        } catch (err) {
            handleApiError(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleFonte(nome: string): Promise<void> {
        reset();
        setLoading(true);
        try {
            const { data } = await createFonte(nome);
            setFontes((prev) => [...prev, data]);
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
                    <FormularioGasto
                        categorias={categorias}
                        loading={loading}
                        success={success}
                        error={error}
                        onSubmit={(descricao, valor, data, categoria) => {
                            void handleGasto(
                                descricao,
                                valor,
                                data,
                                categoria,
                            );
                        }}
                    />
                )}

                {activeTab === "entrada" && (
                    <FormularioEntrada
                        fontes={fontes}
                        loading={loading}
                        success={success}
                        error={error}
                        onSubmit={(descricao, valor, data, fonte) => {
                            void handleEntrada(descricao, valor, data, fonte);
                        }}
                    />
                )}

                {(activeTab === "categoria" || activeTab === "fonte") && (
                    <FormularioCategoriaFonte
                        activeTab={activeTab}
                        loading={loading}
                        success={success}
                        error={error}
                        onSubmit={(nome) => {
                            void (activeTab === "categoria"
                                ? handleCategoria(nome)
                                : handleFonte(nome));
                        }}
                    />
                )}
            </div>
        </div>
    );
}

import { useState, type JSX } from "react";
import { type Categoria } from "../../api/financas";
import { inputStyle, labelStyle, INPUT_CLASS } from "./estilos";
import { SuccessMessage, ErrorMessage } from "./Mensagens";

interface FormularioGastoProps {
    categorias: Categoria[];
    loading: boolean;
    success: string | null;
    error: string | null;
    onSubmit: (
        descricao: string,
        valor: string,
        data: string,
        categoria: string,
    ) => void;
}

export function FormularioGasto({
    categorias,
    loading,
    success,
    error,
    onSubmit,
}: FormularioGastoProps): JSX.Element {
    const [descricao, setDescricao] = useState("");
    const [valor, setValor] = useState("");
    const [data, setData] = useState(new Date().toISOString().slice(0, 10));
    const [categoria, setCategoria] = useState("");

    function handleSubmit(e: React.SyntheticEvent): void {
        e.preventDefault();
        onSubmit(descricao, valor, data, categoria);
        setDescricao("");
        setValor("");
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
                    value={descricao}
                    onChange={(e) => {
                        setDescricao(e.target.value);
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
                        value={valor}
                        onChange={(e) => {
                            setValor(e.target.value);
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
                        value={data}
                        onChange={(e) => {
                            setData(e.target.value);
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
                    value={categoria}
                    onChange={(e) => {
                        setCategoria(e.target.value);
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
    );
}

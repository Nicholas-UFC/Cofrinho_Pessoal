import { type JSX } from "react";

const CARD_BG = "#16213e";
const CARD_BORDER = "1px solid #1e3a5f";

export function GraficoCard({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}): JSX.Element {
    return (
        <div
            style={{ backgroundColor: CARD_BG, border: CARD_BORDER }}
            className="rounded-xl p-6 shadow"
        >
            <h2
                style={{ color: "#f1f5f9" }}
                className="text-base font-semibold mb-4"
            >
                {title}
            </h2>
            {children}
        </div>
    );
}

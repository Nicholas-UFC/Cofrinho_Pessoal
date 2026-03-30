// Declarações de tipos para jest-axe e extensão dos matchers do Vitest

declare module "jest-axe" {
    interface AxeViolation {
        id: string;
        description: string;
        help: string;
        helpUrl: string;
        impact: string | null;
        nodes: unknown[];
    }

    interface AxeResults {
        violations: AxeViolation[];
        passes: unknown[];
        incomplete: unknown[];
        inapplicable: unknown[];
        timestamp: string;
        url: string;
    }

    export function axe(
        element: Element | Document | string,
        options?: Record<string, unknown>,
    ): Promise<AxeResults>;

    export const toHaveNoViolations: Record<
        string,
        (received: AxeResults) => { pass: boolean; message(): string }
    >;
}

declare module "vitest" {
    // Estende o expect do Vitest com o matcher do jest-axe
    interface Assertion<T = unknown> {
        toHaveNoViolations(): T;
    }
}

// Extraído de: LibroCISO/cap-23-testing-grc.md
// tests/accessibility/axe-scan.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const PAGINAS_CRITICAS = [
  { url: "/dashboard", nombre: "Dashboard principal" },
  { url: "/privacy/tratamientos", nombre: "Registro de tratamientos" },
  { url: "/risk/analisis", nombre: "Análisis de riesgos" },
  { url: "/compliance/controles", nombre: "Controles de cumplimiento" },
];

for (const pagina of PAGINAS_CRITICAS) {
  test(`Accesibilidad WCAG 2.1 AA: ${pagina.nombre}`, async ({ page }) => {
    await page.goto(pagina.url);
    // Esperar a que la página cargue completamente
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])  // Nivel AA
      .analyze();

    // Cada violación se reporta con su impacto y el elemento afectado
    const violaciones_criticas = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );

    expect(violaciones_criticas).toHaveLength(0);
  });
}

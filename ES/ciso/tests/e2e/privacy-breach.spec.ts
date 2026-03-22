// Extraído de: LibroCISO/cap-23-testing-grc.md
// tests/e2e/privacy-breach.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Gestión de brechas — flujo completo", () => {
  test("DPO crea brecha, verifica plazo 72h y exporta informe", async ({
    page,
  }) => {
    // Login como DPO
    await page.goto("/login");
    await page.fill('[data-testid="email"]', "dpo@test.ejemplo.es");
    await page.fill('[data-testid="password"]', "TestPassword123!");
    await page.click('[data-testid="login-submit"]');
    await expect(page).toHaveURL("/dashboard");

    // Navegar al módulo de brechas
    await page.click('[data-testid="nav-privacy"]');
    await page.click('[data-testid="nav-brechas"]');

    // Crear nueva brecha
    await page.click('[data-testid="btn-nueva-brecha"]');
    await page.fill('[data-testid="titulo"]', "Test: acceso no autorizado");
    await page.fill('[data-testid="fecha-deteccion"]', "2025-03-15T10:00");
    await page.fill('[data-testid="datos-afectados"]', "Datos identificativos");
    await page.fill('[data-testid="num-afectados"]', "50");
    await page.click('[data-testid="btn-guardar"]');

    // Verificar que el indicador de plazo aparece
    await expect(page.locator('[data-testid="plazo-72h-badge"]')).toBeVisible();

    // Exportar informe para la AEPD
    await page.click('[data-testid="btn-exportar-aepd"]');
    const download = await page.waitForEvent("download");
    expect(download.suggestedFilename()).toContain("brecha");
    expect(download.suggestedFilename()).toMatch(/\.(pdf|docx)$/);
  });

  test("Analyst NO puede crear brechas (segregación de funciones)", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.fill('[data-testid="email"]', "analyst@test.ejemplo.es");
    await page.fill('[data-testid="password"]', "TestPassword123!");
    await page.click('[data-testid="login-submit"]');

    await page.goto("/privacy/brechas/new");
    // El sistema debe redirigir o mostrar error de permisos
    await expect(page.locator('[data-testid="error-permisos"]')).toBeVisible();
  });
});

# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: tarea de automatización con reintentos agresivos
# Patrón: tasks/automation/portal_bot.py

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(
    bind=True,
    base=AutomationTask,
    queue="automation",
    time_limit=14400,      # 4 horas máximo absoluto
    soft_time_limit=13800, # Señal de aviso a las 3h50m
)
def run_portal_automation(self, operation_id: str, params: dict):
    """
    Ejecuta una sesión de automatización contra el portal corporativo.
    Gestiona reintentos ante mantenimientos y expiración de sesión.
    """
    from automation.drivers import SeleniumDriver

    try:
        driver = SeleniumDriver(
            grid_url="http://selenium-hub:4444/wd/hub",
            browser="chrome",
            timeout=30,
        )
        session = driver.authenticate(
            username=get_portal_credential("username"),
            password=get_portal_credential("password"),
        )
        result = session.execute_operation(params)
        log_automation_result(operation_id, result)
        return {"status": "completed", "operation_id": operation_id}

    except PortalMaintenanceException:
        raise self.retry(countdown=60)
    except SessionExpiredException:
        raise self.retry(countdown=30)
    except SoftTimeLimitExceeded:
        save_partial_state(operation_id)
        raise self.retry(countdown=300)
    finally:
        if "driver" in locals():
            driver.quit()

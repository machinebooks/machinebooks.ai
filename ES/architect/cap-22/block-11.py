# Extraído de: LibroTecnico/cap-22-observabilidad.md
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader
import pyotp

class EmailService:
    """Servicio de email con templates HTML y soporte OTP.

    Configurable por variables de entorno — no hay valores hardcodeados.
    El servidor SMTP puede ser corporativo, SendGrid, AWS SES o cualquier
    proveedor que soporte autenticación SMTP.
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM_ADDRESS")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "la Plataforma")

        # Motor de plantillas Jinja2 desde directorio de templates
        self.jinja_env = Environment(
            loader=PackageLoader("email_templates", "templates"),
            autoescape=True
        )

    def send_otp_for_critical_operation(
        self,
        user_email: str,
        operation_type: str,
        operation_context: dict,
        client_ip: str
    ) -> str:
        """Envía OTP para confirmar una operación crítica de configuración.

        Se usa para: cambios de configuración IA, modificación de presupuestos,
        rotación de credenciales del vault, cambios en permisos admin.

        El OTP tiene validez de 10 minutos y uso único.
        """
        # Genera OTP de 6 dígitos con TOTP (válido 10 minutos)
        totp = pyotp.TOTP(
            s=os.getenv("OTP_SECRET_KEY"),
            interval=600  # 10 minutos
        )
        otp_code = totp.now()

        # Contexto para la plantilla de email
        template_context = {
            "otp_code": otp_code,
            "operation_type": operation_type,
            "operation_description": operation_context.get("description", ""),
            "client_ip": client_ip,
            "valid_minutes": 10,
            "timestamp": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
        }

        self._send_template_email(
            to_email=user_email,
            subject=f"Código de verificación — {operation_type}",
            template_name="critical_operation_otp.html",
            context=template_context
        )

        # Registra en auditoría que se envió un OTP para esta operación
        log_audit_event(
            action=AuditActions.AI_CONFIG_CHANGED,
            details={
                "event": "otp_sent",
                "operation_type": operation_type,
                "ip": client_ip
            },
            severity="WARNING"
        )

        return otp_code  # Solo para validación interna — no se loguea

    def _send_template_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: dict
    ) -> None:
        """Envía email con plantilla HTML usando el servidor SMTP configurado."""

        template = self.jinja_env.get_template(template_name)
        html_body = template.render(**context)

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.smtp_user, self.smtp_password)
            smtp.send_message(msg)

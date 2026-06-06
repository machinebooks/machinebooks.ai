# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/sso.py — MFA enforcement after SSO success
mfa_required = bool(user.mfa_enabled)
if mfa_required:
    await MFAService.send_code(redis, user.id, user.email, user.name)
    # Only expose the email domain (anti-enumeration)
    email_domain = user.email.split("@", 1)[-1] if "@" in user.email else ""
    body = json.dumps({
        "type": "sso_callback_mfa",
        "mfa_required": True,
        "user_id": user.id,
        "email_domain": email_domain,  # not the full email
    })
    return HTMLResponse(f"""
    <html><body><script>
        var data = JSON.parse({json.dumps(body)});
        window.opener?.postMessage(data, window.location.origin);
        window.close();
    </script>
    <p>Additional verification required. Check your email.</p>
    </body></html>
    """)

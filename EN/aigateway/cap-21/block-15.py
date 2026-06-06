# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
snapshot_json = json.dumps(snapshot, ensure_ascii=False, default=str)
if len(snapshot_json) > 60_000:
    snapshot_json = snapshot_json[:60_000] + "\n...TRUNCATED..."

# Prompts from DB (zero hardcoding)
system_prompt = await PromptService.get("audit.report_system", db)
user_template = await PromptService.get("audit.report_user_template", db)
user_prompt = user_template.replace("{snapshot_json}", snapshot_json)

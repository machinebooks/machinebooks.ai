# Extraído de: LibroFinOps/cap-06-atribucion.md
# services/aws_cost_categories.py
import boto3

def create_cost_category(category_name: str, rules: list[dict]) -> dict:
    """
    Crea una Cost Category en AWS Cost Explorer.
    Las reglas mapean tags de recursos a valores de la categoría.
    Ejemplo: todos los recursos con tag team=backend -> "Equipo Backend"
    """
    ce_client = boto3.client("ce", region_name="us-east-1")

    response = ce_client.create_cost_category_definition(
        Name=category_name,
        RuleVersion="CostCategoryExpression.v1",
        Rules=rules,
        DefaultValue="Sin atribuir",
    )

    return response["CostCategoryArn"]


def build_team_category_rules() -> list[dict]:
    """
    Construye las reglas de la Cost Category por equipo.
    Una regla por valor del tag 'team'.
    """
    teams = {
        "backend": "Equipo Backend",
        "frontend": "Equipo Frontend",
        "data": "Equipo Datos",
        "platform": "Equipo Plataforma",
        "security": "Equipo Seguridad",
    }

    rules = []
    for tag_value, category_value in teams.items():
        rules.append({
            "Value": category_value,
            "Rule": {
                "Tags": {
                    "Key": "team",
                    "Values": [tag_value],
                    "MatchOptions": ["EQUALS"],
                }
            },
        })

    return rules


def get_cost_by_category(category_name: str, start_date: str, end_date: str) -> list[dict]:
    """
    Consulta el gasto agrupado por Cost Category en el período dado.
    start_date y end_date en formato YYYY-MM-DD.
    """
    ce_client = boto3.client("ce", region_name="us-east-1")

    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "COST_CATEGORY",
                "Key": category_name,
            }
        ],
    )

    results = []
    for time_period in response["ResultsByTime"]:
        for group in time_period["Groups"]:
            results.append({
                "period": time_period["TimePeriod"]["Start"],
                "category_value": group["Keys"][0],
                "cost_usd": float(group["Metrics"]["UnblendedCost"]["Amount"]),
                "currency": group["Metrics"]["UnblendedCost"]["Unit"],
            })

    return results

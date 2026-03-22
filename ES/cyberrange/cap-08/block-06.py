# Extraído de: LibroCyberrange/cap-08-workzones.md
# El listado filtra por workzone del usuario
if current_user.role == "admin":
    workzones = db.query(Workzone).all()
else:
    workzones = db.query(Workzone).filter(
        Workzone.id == current_user.workzone_id
    ).all()

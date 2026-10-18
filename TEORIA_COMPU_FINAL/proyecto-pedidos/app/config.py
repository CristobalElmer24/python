import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-tc-pedidos")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB
    ENUNCIADO = (
        "Automatización del proceso de pedidos mediante un analizador léxico y "
        "sintáctico para reducir errores de registro en restaurantes con atención "
        "en mesa, para llevar y delivery."
    )
    EJEMPLO = (
        "PED-045-M12-C03\n"
        "PED-102-D-B02+S01\n"
        "PED-007-L-C01+B02+S03\n"
        "PED-45-M12-C03\n"
        "PED-045-M12-Z99\n"
        "PED-000-M12-C03"
    )

import oracledb

# Configuración de conexión a la base de datos de la UGR
dsn = oracledb.makedsn("oracle0.ugr.es", "1521", service_name="PRACTBD")
user = "x8005552"
password = "cooper15"

# Establece la conexión a la BD y devuelve la conexión para poder hacer consultas desde otras clases
def conectar():
    try:
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        print("Conectado a Oracle")
        return connection
    except oracledb.DatabaseError as e:
        print("Error de conexión:", e)
        return None

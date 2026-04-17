import sqlite3

def list_accountants():
    conn = sqlite3.connect('motor_dev.db')
    cursor = conn.cursor()
    try:
        # Nota: Ajustamos nombres de columnas según el modelo SQLAlchemy
        cursor.execute("SELECT id, email, nombre_completo, rol FROM usuarios WHERE rol = 'CONTADOR'")
        accountants = cursor.fetchall()
        if not accountants:
            print("No se encontraron usuarios con el rol CONTADOR.")
        else:
            for acc in accountants:
                print(f"ID: {acc[0]} | Email: {acc[1]} | Nombre: {acc[2]} | Rol: {acc[3]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_accountants()

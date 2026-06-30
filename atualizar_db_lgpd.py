import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE inscricoes
        ADD COLUMN termo_lgpd TEXT DEFAULT 'Sim'
    """)

    conn.commit()
    print("Coluna termo_lgpd adicionada com sucesso.")

except sqlite3.OperationalError as erro:
    if "duplicate column name" in str(erro):
        print("A coluna termo_lgpd já existe.")
    else:
        print("Erro ao atualizar banco:")
        print(erro)

conn.close()
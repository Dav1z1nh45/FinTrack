from pathlib import Path
import sqlite3
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fintrack.db"


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    with conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
                descricao TEXT NOT NULL,
                categoria TEXT NOT NULL,
                valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
                data TEXT NOT NULL,
                observacoes TEXT NOT NULL DEFAULT ''
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data)")


def criar_transacao(tipo, descricao, categoria, valor_centavos, data_transacao=None, observacoes=""):
    if tipo not in ("Receita", "Despesa"):
        raise ValueError("Tipo inválido.")
    if not descricao.strip():
        raise ValueError("A descrição não pode ficar vazia.")
    if not categoria.strip():
        raise ValueError("A categoria não pode ficar vazia.")
    if not isinstance(valor_centavos, int) or valor_centavos <= 0:
        raise ValueError("O valor deve ser positivo e informado em centavos.")
    data_transacao = data_transacao or date.today().isoformat()
    date.fromisoformat(data_transacao)
    with conectar() as con:
        cursor = con.execute("""
            INSERT INTO transacoes (tipo, descricao, categoria, valor_centavos, data, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tipo, descricao.strip(), categoria.strip(), valor_centavos,
              data_transacao, observacoes.strip()))
        return cursor.lastrowid


def listar_transacoes(inicio=None, fim=None):
    consulta = "SELECT * FROM transacoes"
    filtros = []
    parametros = []
    if inicio:
        filtros.append("data >= ?")
        parametros.append(inicio)
    if fim:
        filtros.append("data <= ?")
        parametros.append(fim)
    if filtros:
        consulta += " WHERE " + " AND ".join(filtros)
    consulta += " ORDER BY data DESC, id DESC"
    with conectar() as con:
        return [dict(row) for row in con.execute(consulta, parametros).fetchall()]


def buscar_transacao(transacao_id):
    with conectar() as con:
        row = con.execute("SELECT * FROM transacoes WHERE id = ?", (transacao_id,)).fetchone()
        return dict(row) if row else None


def atualizar_transacao(transacao_id, tipo, descricao, categoria, valor_centavos, data_transacao, observacoes=""):
    if tipo not in ("Receita", "Despesa"):
        raise ValueError("Tipo inválido.")
    if not descricao.strip() or not categoria.strip():
        raise ValueError("Descrição e categoria são obrigatórias.")
    if not isinstance(valor_centavos, int) or valor_centavos <= 0:
        raise ValueError("O valor deve ser positivo.")
    date.fromisoformat(data_transacao)
    with conectar() as con:
        cursor = con.execute("""
            UPDATE transacoes
            SET tipo = ?, descricao = ?, categoria = ?, valor_centavos = ?, data = ?, observacoes = ?
            WHERE id = ?
        """, (tipo, descricao.strip(), categoria.strip(), valor_centavos,
              data_transacao, observacoes.strip(), transacao_id))
        return cursor.rowcount > 0


def excluir_transacao(transacao_id):
    with conectar() as con:
        cursor = con.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
        return cursor.rowcount > 0

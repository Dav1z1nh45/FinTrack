import database as db


def test_create_list_and_delete_transaction(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.inicializar_banco()

    transaction_id = db.criar_transacao(
        tipo="Despesa",
        descricao="Livro",
        categoria="Educação",
        valor_centavos=4590,
        data_transacao="2026-10-29",
        observacoes="Teste",
    )

    transaction = db.buscar_transacao(transaction_id)
    assert transaction is not None
    assert transaction["descricao"] == "Livro"
    assert transaction["valor_centavos"] == 4590

    transactions = db.listar_transacoes("2026-10-01", "2026-10-31")
    assert len(transactions) == 1

    assert db.excluir_transacao(transaction_id) is True
    assert db.buscar_transacao(transaction_id) is None


def test_reject_invalid_amount(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.inicializar_banco()

    try:
        db.criar_transacao("Despesa", "Teste", "Outros", 0, "2026-10-29")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero amount")

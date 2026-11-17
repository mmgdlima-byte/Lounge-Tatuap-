
import os
import sys

import pytest

# Usa um banco temporário, separado do banco real do projeto.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-de-teste"

sys.path.insert(0, os.path.abspath("lounge-tatuape"))

from app import app, db, Order


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(
            Order(
                region="São Paulo - SP",
                carrier="Transportadora Teste",
                tracking_code="TESTE123",
            )
        )
        db.session.commit()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_pagina_login(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_com_senha_correta(client):
    response = client.post(
        "/",
        data={"username": "admin", "password": "lounge123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Pedidos" in response.data or b"pedidos" in response.data


def test_login_com_senha_incorreta(client):
    response = client.post(
        "/",
        data={"username": "admin", "password": "senhaerrada"},
    )
    assert response.status_code == 200


def test_pedidos_exige_login(client):
    response = client.get("/pedidos")
    assert response.status_code == 302


def test_pedidos_com_login(client):
    with client.session_transaction() as session:
        session["logged_in"] = True

    response = client.get("/pedidos")
    assert response.status_code == 200


def test_consultar_pedido(client):
    with client.session_transaction() as session:
        session["logged_in"] = True

    response = client.get("/consultar?q=TESTE123")
    assert response.status_code == 200
    assert b"TESTE123" in response.data


def test_registrar_ocorrencia(client):
    with client.session_transaction() as session:
        session["logged_in"] = True

    with app.app_context():
        order = Order.query.filter_by(tracking_code="TESTE123").first()
        order_id = order.id

    response = client.post(
        "/alertas",
        data={"order_id": order_id, "occurrence": "Teste de ocorrência"},
    )

    assert response.status_code == 302

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.occurrence == "Teste de ocorrência"


def test_atualizar_status(client):
    with client.session_transaction() as session:
        session["logged_in"] = True

    with app.app_context():
        order = Order.query.filter_by(tracking_code="TESTE123").first()
        order_id = order.id

    response = client.post(
        f"/status/{order_id}",
        data={"status": "Entregue"},
    )

    assert response.status_code == 302

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == "Entregue"


def test_sair(client):
    with client.session_transaction() as session:
        session["logged_in"] = True

    response = client.get("/sair")
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "logged_in" not in session

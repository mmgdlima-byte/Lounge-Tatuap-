
import os
from datetime import date
from functools import wraps

from flask import (
    Flask, flash, redirect, render_template,
    request, session, url_for
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configurações principais
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "troque-esta-chave-em-producao"
)

database_url = os.getenv(
    "DATABASE_URL", "sqlite:///lounge_tatuape.db"
)

# Compatibilidade com PostgreSQL e Psycopg 3
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Segurança dos cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("FLASK_ENV") == "production"
)

db = SQLAlchemy(app)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    carrier = db.Column(db.String(100), nullable=False)
    tracking_code = db.Column(
        db.String(100), unique=True, nullable=False
    )
    order_date = db.Column(
        db.Date, nullable=False, default=date.today
    )
    status = db.Column(
        db.String(30), nullable=False, default="Em andamento"
    )
    occurrence = db.Column(db.String(255), nullable=True)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        expected_user = os.getenv("DEMO_USER", "admin")
        expected_password = os.getenv(
            "DEMO_PASSWORD", "lounge123"
        )

        if username == expected_user and check_password_hash(
            generate_password_hash(expected_password), password
        ):
            session.clear()
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("pedidos"))

        flash(
            "Usuário ou senha inválidos. Confira os dados e tente novamente.",
            "error"
        )

    return render_template("login.html")


@app.route("/pedidos", methods=["GET", "POST"])
@login_required
def pedidos():
    if request.method == "POST":
        region = request.form.get("region", "").strip()
        carrier = request.form.get("carrier", "").strip()
        tracking_code = request.form.get(
            "tracking_code", ""
        ).strip()
        order_date = request.form.get("order_date", "").strip()

        if not all([region, carrier, tracking_code, order_date]):
            flash("Preencha todos os campos obrigatórios.", "error")
        else:
            try:
                parsed_date = date.fromisoformat(order_date)

                order = Order(
                    region=region,
                    carrier=carrier,
                    tracking_code=tracking_code,
                    order_date=parsed_date
                )

                db.session.add(order)
                db.session.commit()

                flash("Pedido cadastrado com sucesso!", "success")
                return redirect(url_for("pedidos"))

            except ValueError:
                db.session.rollback()
                flash("Informe uma data válida.", "error")

            except Exception:
                db.session.rollback()
                flash(
                    "Não foi possível cadastrar. Verifique se o código já existe.",
                    "error"
                )

    return render_template(
        "pedidos.html",
        active="pedidos",
        today=date.today().isoformat()
    )


@app.route("/consultar")
@login_required
def consultar():
    term = request.args.get("q", "").strip()
    query = Order.query

    if term:
        query = query.filter(
            Order.tracking_code.ilike(f"%{term}%")
        )

    orders = query.order_by(Order.id.desc()).all()

    return render_template(
        "alertas.html",
        active="consultar",
        orders=orders,
        title="Consultar Pedidos"
    )


@app.route("/alertas", methods=["GET", "POST"])
@login_required
def alertas():
    if request.method == "POST":
        order_id = request.form.get("order_id", type=int)
        note = request.form.get("occurrence", "").strip()

        order = db.session.get(Order, order_id) if order_id else None

        if order and note:
            order.occurrence = note
            db.session.commit()
            flash("Ocorrência registrada com sucesso!", "success")
        else:
            flash(
                "Selecione um pedido e descreva a ocorrência.",
                "error"
            )

        return redirect(url_for("alertas"))

    status = request.args.get("status", "")
    query = Order.query

    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.id.desc()).all()

    return render_template(
        "alertas.html",
        active="alertas",
        orders=orders,
        title="Alertas e Ocorrências",
        selected_status=status
    )


@app.route("/status/<int:order_id>", methods=["POST"])
@login_required
def update_status(order_id):
    order = db.session.get(Order, order_id)
    status = request.form.get("status", "")

    allowed = {
        "Em andamento",
        "Entregue",
        "Em atraso",
        "Extraviado"
    }

    if order and status in allowed:
        order.status = status
        db.session.commit()
        flash("Status atualizado com sucesso!", "success")
    else:
        flash("Não foi possível atualizar o status.", "error")

    return redirect(request.referrer or url_for("alertas"))


@app.route("/sair")
def logout():
    session.clear()
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()

    # Dados de demonstração somente fora de produção
    if os.getenv("FLASK_ENV") != "production":
        if Order.query.count() == 0:
            db.session.add_all([
                Order(
                    region="São Paulo - SP",
                    carrier="Transportadora Expressa",
                    tracking_code="TRK1001",
                    order_date=date.today(),
                    status="Entregue"
                ),
                Order(
                    region="Rio de Janeiro - RJ",
                    carrier="LogiRápido",
                    tracking_code="TRK1002",
                    order_date=date.today(),
                    status="Em atraso",
                    occurrence="Entrega prevista não realizada"
                ),
                Order(
                    region="Minas Gerais - MG",
                    carrier="Entrega Já",
                    tracking_code="TRK1003",
                    order_date=date.today(),
                    status="Extraviado",
                    occurrence="Aguardando análise"
                )
            ])
            db.session.commit()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") != "production")

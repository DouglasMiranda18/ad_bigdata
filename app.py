import os
import sqlite3
from contextlib import closing
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.root_path, "casamento.db")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")


WEDDING_INFO = {
    "noiva": "Manuella",
    "noivo": "Douglas",
    "data": "02/05/2026",
    "igreja": "Nossa Senhora do Bom Parto",
    "hora": "A definir",
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "guest_id" not in session:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def init_db():
    db = get_db()
    with closing(open("schema.sql", "r", encoding="utf-8")) as f:
        db.executescript(f.read())

    guests = [
        ("Ana Paula", "1234"),
        ("Carlos Silva", "5678"),
        ("Fernanda Lima", "9999"),
    ]
    gifts = [
        ("Jogo de panelas", 45000),
        ("Aparelho de jantar", 38000),
        ("Air fryer", 60000),
        ("Cafeteira", 30000),
        ("Conjunto de taças", 20000),
    ]

    db.executemany("INSERT INTO guests (name, password) VALUES (?, ?)", guests)
    db.executemany("INSERT INTO gifts (name, price_cents) VALUES (?, ?)", gifts)
    db.commit()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        guest = db.execute(
            "SELECT id, name FROM guests WHERE LOWER(name) = LOWER(?) AND password = ?",
            (name, password),
        ).fetchone()

        if guest is None:
            flash("Nome ou senha inválidos.", "error")
        else:
            session.clear()
            session["guest_id"] = guest["id"]
            session["guest_name"] = guest["name"]
            return redirect(url_for("invite"))

    return render_template("login.html")


@app.route("/convite")
@login_required
def invite():
    return render_template("invite.html", wedding=WEDDING_INFO)


@app.route("/lista-presentes", methods=["GET", "POST"])
@login_required
def gifts_list():
    db = get_db()

    if request.method == "POST":
        gift_id = request.form.get("gift_id", type=int)
        payment_method = request.form.get("payment_method", "")

        gift = db.execute("SELECT * FROM gifts WHERE id = ?", (gift_id,)).fetchone()
        if gift is None:
            flash("Presente não encontrado.", "error")
        elif gift["reserved_by"] is not None:
            flash("Esse item já foi reservado.", "error")
        elif payment_method not in {"pix", "cartao"}:
            flash("Selecione uma forma de pagamento válida.", "error")
        else:
            db.execute(
                "UPDATE gifts SET reserved_by = ?, payment_method = ? WHERE id = ? AND reserved_by IS NULL",
                (session["guest_id"], payment_method, gift_id),
            )
            db.commit()
            if db.total_changes == 0:
                flash("Não foi possível reservar. Atualize a página.", "error")
            else:
                if payment_method == "pix":
                    flash(
                        "Item reservado! Faça o Pix para chave exemplo@casamento.com.",
                        "success",
                    )
                else:
                    flash(
                        "Item reservado! Integração de cartão será conectada com a API escolhida.",
                        "success",
                    )

    gifts = db.execute(
        """
        SELECT g.id, g.name, g.price_cents, g.payment_method, guest.name AS reserved_by_name
        FROM gifts g
        LEFT JOIN guests guest ON guest.id = g.reserved_by
        ORDER BY g.id
        """
    ).fetchall()

    return render_template("gifts.html", gifts=gifts)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Banco inicializado com dados de exemplo.")


if __name__ == "__main__":
    app.run(debug=True)

# Start debugserver this way: FLASK_DEBUG=1 python -m flask run

from flask import Flask, redirect, url_for, flash, render_template
from flask_login import login_required, logout_user
from .config import Config
from .models import db, login_manager
from .oauth import blueprint
from .cli import create_db
from .views.home import home_blueprint
from .views.mail import mail_blueprint
from .views.person import person_blueprint
from .views.lister import lister_blueprint

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config)
app.register_blueprint(home_blueprint)
app.register_blueprint(blueprint, url_prefix="/login")
app.register_blueprint(mail_blueprint, url_prefix="/mail")
app.register_blueprint(person_blueprint, url_prefix="/person")
app.register_blueprint(lister_blueprint, url_prefix="/lister")
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)

print(app.config)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du er nu logget ud!")
    return redirect(url_for("home.home"))

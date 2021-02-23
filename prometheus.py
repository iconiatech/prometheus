import sys
import yaml
import json
import base64
import configparser

from datetime import datetime
from flask import (
    Flask,
    flash,
    request,
    url_for,
    redirect,
    render_template)
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
            LoginManager,
            UserMixin,
            login_user,
            current_user,
            logout_user,
            login_required)

app = Flask(__name__)
app.config["SECRET_KEY"] = "5791fcasxth5899863986498hggshdf"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@db/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app=app)
bcrypt = Bcrypt(app=app)
login_manager = LoginManager(app=app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


class User(db.Model, UserMixin):
    """

    """

    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    suspended = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_id(self):
        return (self.user_id)


class Exporter(db.Model):

    exporter_code = db.Column(db.Integer, primary_key=True)
    exporter_name = db.Column(db.String(100), nullable=False)
    exporter_description = db.Column(db.String(200), nullable=False)
    exporter_metric_path = db.Column(db.String(100), nullable=True)
    exporter_module = db.Column(db.String(100), nullable=True)
    relabel_port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='exporter', lazy=True)

    def __repr__(self):
        return f"Exporter '{self.exporter_name}'"


class Job(db.Model):

    job_code = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(100), unique=True, nullable=False)
    scrape_interval = db.Column(db.Integer, nullable=False, default=15)
    exporter_code = db.Column(db.Integer, db.ForeignKey('exporter.exporter_code'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    labels = db.relationship('Label', backref='label', lazy=True)

    def __repr__(self):
        return f"Job '{self.job_name}'"


class Label(db.Model):

    label_code = db.Column(db.Integer, primary_key=True)
    label_key = db.Column(db.String(100), nullable=False)
    label_value = db.Column(db.String(100), nullable=True)
    job_code = db.Column(db.Integer, db.ForeignKey('job.job_code'), nullable=False)
    target_code = db.Column(db.Integer, db.ForeignKey('target.target_code'), nullable=True)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    job = db.relationship('Job', backref='job_label', lazy=True)
    target = db.relationship('Target', backref='labels', lazy=True)

    def __repr__(self):
        return f"Label '{self.label_key}' - '{self.label_value}'"


class JobLabel(db.Model):

    jb_lb_code = db.Column(db.Integer, primary_key=True)
    label_key = db.Column(db.String(100), nullable=False)
    job_code = db.Column(db.Integer, db.ForeignKey('job.job_code'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    job = db.relationship('Job', backref='jb_lb', lazy=True)


class Target(db.Model):

    target_code = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), nullable=False)
    job_code = db.Column(db.Integer, db.ForeignKey('job.job_code'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    job = db.relationship('Job', backref='targets', lazy=True)

    def __repr__(self):
        return f"Target '{self.target_name}'"


@login_manager.user_loader
def load_user(user_id):
    """

    """

    return User.query.get(int(user_id))

@app.before_first_request
def initialize_requirements():
    """

    """

    try:

        db.create_all()
        exporters = Exporter.query.filter_by().all()

        with open("./exporters.json") as f:
            data = json.load(f)

            if not exporters:
                for row in data:
                    exporter = Exporter(
                                relabel_port=row["port"],
                                exporter_name=row["name"],
                                exporter_module=row["module"],
                                exporter_description=row["desc"],
                                exporter_metric_path=row["metric"])

                    db.session.add(exporter)
                    db.session.commit()

    except Exception as error:
        print(error)

@app.route("/register", methods=["GET", "POST"])
def register():
    """

    """

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        error = ""

        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            error = "Username already taken!"

        user = User.query.filter_by(email=email).first()

        if user:
            error = "Email already in use!"

        if error:
            flash(error, "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(
                                    password).decode("utf-8")

        user = User(
                email=email, 
                username=username, 
                password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash("Your account has been created. You are now able to login", "success")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    """

    """

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get("next")
            flash("Login Successful. Welcome Back!", "success")
            return redirect(next_page) if next_page else redirect(url_for("index"))

        flash("Login Unsuccessful. Please check email and password.", "danger")

    return render_template("login.html" , title="Login")

@app.route("/logout")
def logout():
    """

    """

    logout_user()
    return redirect(url_for("index"))

@app.route("/")
@app.route("/home", methods=["GET"])
@login_required
def index():
    """

    """

    jobs = Job.query.filter_by(status=1, deleted=0).all()
    labels = Label.query.filter_by(status=1, deleted=0).all()
    targets = Target.query.filter_by(status=1, deleted=0).all()

    summary = {
        "jobs": len(jobs),
        "labels": len(labels),
        "targets": len(targets),
    }

    return render_template(
        "home.html",
        title="Home",
        targets=targets,
        summary=summary,)

@app.route("/add-new", methods=["GET", "POST"])
@login_required
def add_new():
    """

    """

    jobs = Job.query.filter_by(status=1, deleted=0).all()
    exporters = Exporter.query.filter_by(status=1, deleted=0).all()

    if request.method == "POST":
        job_code = request.form["job"]

        if int(job_code) == 0:
            flash("Please select a job", "warning")
            return redirect(url_for("add_new"))

        return redirect(url_for("home_targets", job_code=job_code))

    return render_template(
        "add_new.html",
        jobs=jobs,
        exporters=exporters,
        title="Add New Targets",
        )

@app.route("/home/create/<int:job_code>", methods=["GET", "POST"])
@login_required
def home_targets(job_code: int):
    """

    """

    job = Job.query.get_or_404(job_code)
    labels = JobLabel.query.filter_by(
                            job_code=job_code,
                            status=1,
                            deleted=0).all()
    targets = Target.query.filter_by(
                            job_code=job_code,
                            status=1,
                            deleted=0).all()

    if request.method == "POST":

        read_config = configparser.ConfigParser()
        read_config.read("configs.ini")

        limit = read_config.get("LICENCES", "targets")

        data = base64.b64decode(limit).decode("UTF-8")

        if len(targets) >= int(data):
            flash("You have exceeded the limit of targets as per licence", "danger")
            return redirect(url_for("home_targets", job_code=job_code))

        target_name = request.form["target-name"]
        check_exists = Target.query.filter_by(
                            target_name=target_name,
                            job_code=job_code,
                            status=1,
                            deleted=0).all()

        if check_exists:

            flash(f"Target '{target_name}' already exists!", "danger")
            return redirect(url_for("home_targets", job_code=job_code))

        target = Target(
                    target_name=target_name,
                    job_code=job_code)

        db.session.add(target)
        db.session.commit()

        form_data = dict(request.form)
        
        for label in labels:

            label_value = form_data.get(label.label_key)

            new_label = Label(
                            label_key=label.label_key,
                            label_value=label_value,
                            job_code=job_code,
                            target_code=target.target_code)

            db.session.add(new_label)

        db.session.commit()

        flash("Target and labels successfully added!", "success")
        return redirect(url_for("home_targets", job_code=job_code))

    return render_template(
        "home_targets.html",
        job=job,
        labels=labels,
        targets=targets,
        title="Add Targets",
        )

@app.route("/home/jobs/update", methods=["POST"])
@login_required
def home_jobs_update():
    """

    """

    if request.method == "POST":

        scrape = request.form["scrape"]
        job_name = request.form["job_name"]
        exporter = request.form["exporter"]

        check_exists = Job.query.filter_by(
                            job_name=job_name).all()

        if check_exists:

            flash(f"Job '{job_name}' already exists!", "danger")
            return redirect(url_for("add_new"))

        job = Job(
                job_name=job_name,
                scrape_interval=scrape,
                exporter_code=exporter)

        db.session.add(job)
        db.session.commit()

        flash("Job has been successfully created!", "success")
        return redirect(url_for("add_new"))

@app.route("/home/labels/update/<int:job_code>", methods=["POST"])
@login_required
def home_labels_update(job_code: int):
    """

    """

    if request.method == "POST":

        label_key = request.form["label-key"]

        check_exists = JobLabel.query.filter_by(
                                label_key=label_key,
                                job_code=job_code).all()

        if check_exists:
            flash(f"Label '{label_key}' already exists!", "danger")
            return redirect(url_for("home_targets", job_code=job_code))

        label = JobLabel(
                label_key=label_key,
                job_code=job_code)

        db.session.add(label)
        db.session.commit()

        flash("Label successfully added", "success")
        return redirect(url_for("home_targets", job_code=job_code))

@app.route("/jobs", methods=["GET", "POST"])
@login_required
def jobs():

    if request.method == "POST":

        scrape = request.form["scrape"]
        job_name = request.form["job_name"]
        exporter = request.form["exporter"]

        check_exists = Job.query.filter_by(
                            job_name=job_name).all()

        if check_exists:

            flash(f"Job '{job_name}' already exists!", "danger")
            return redirect(url_for("jobs"))

        job = Job(
                job_name=job_name,
                scrape_interval=scrape,
                exporter_code=exporter)

        db.session.add(job)
        db.session.commit()

        flash("Job has been successfully created!", "success")

    jobs = Job.query.filter_by(status=1, deleted=0).all()
    inactive_jobs = Job.query.filter_by(status=0, deleted=0).all()
    exporters = Exporter.query.filter_by(status=1, deleted=0).all()

    summary = {
        "all": len(jobs),
        "active": len(jobs),
        "inactive": len(inactive_jobs),
    }

    return render_template(
                "jobs.html",
                jobs=jobs,
                title="Jobs",
                summary=summary,
                exporters=exporters)

@app.route("/labels", methods=["GET", "POST"])
@login_required
def labels():

    jobs = Job.query.filter_by(status=1).all()
    labels = JobLabel.query.filter_by(status=1).all()
    summary = {
        "all": len(labels),
        "active": len(labels),
        "inactive": 0,
    }

    if request.method == "POST":

        job_code = request.form["job_code"]
        label_key = request.form["label_key"]

        check_exists = JobLabel.query.filter_by(
                                label_key=label_key,
                                job_code=job_code).all()

        if check_exists:
            flash(f"Label '{label_key}' already exists!", "danger")

            return render_template(
                "labels.html",
                jobs=jobs,
                title="Labels",
                summary=summary,
                labels=labels)

        label = JobLabel(
                label_key=label_key,
                job_code=job_code)

        db.session.add(label)
        db.session.commit()

        flash("Label has been successfully created!", "success")

    jobs = Job.query.filter_by(status=1).all()
    labels = JobLabel.query.filter_by(status=1).all()
    summary = {
        "all": len(labels),
        "active": len(labels),
        "inactive": 0,
    }

    return render_template(
                "labels.html",
                jobs=jobs,
                title="Labels",
                summary=summary,
                labels=labels)

@app.route("/targets", methods=["GET", "POST"])
@login_required
def targets():

    if request.method == "POST":

        job_code = request.form["job_code"]

        return redirect(url_for("new_target", job_code=job_code))

    jobs = Job.query.filter_by(status=1).all()
    targets = Target.query.filter_by(status=1).all()
    summary = {
        "all": len(targets),
        "active": len(targets),
        "inactive": 0,
    }

    return render_template(
                "targets.html",
                jobs=jobs,
                title="Targets",
                summary=summary,
                targets=targets)

@app.route("/target/new/<int:job_code>", methods=["GET", "POST"])
@login_required
def new_target(job_code: int):

    job = Job.query.get_or_404(job_code)
    labels = JobLabel.query.filter_by(
                            job_code=job_code,
                            status=1).all()
    targets = Target.query.filter_by(status=1).all()

    if request.method == "POST":

        read_config = configparser.ConfigParser()
        read_config.read("configs.ini")

        limit = read_config.get("LICENCES", "targets")

        data = base64.b64decode(limit).decode("UTF-8")

        if len(targets) >= int(data):
            flash("You have exceeded the limit of targets as per licence", "warning")
            return redirect(url_for("targets"))

        target_name = request.form["target_name"]
        check_exists = Target.query.filter_by(
                            target_name=target_name,
                            job_code=job_code,
                            status=1).all()

        if check_exists:

            flash(f"Target '{target_name}' already exists!", "warning")
            return render_template(
                        "target.html",
                        job=job,
                        labels=labels,
                        title=f"Add Targets - {job.job_name}",)

        target = Target(
                    target_name=target_name,
                    job_code=job_code)

        db.session.add(target)
        db.session.commit()

        form_data = dict(request.form)
        
        for label in labels:

            label_value = form_data.get(label.label_key)

            new_label = Label(
                            label_key=label.label_key,
                            label_value=label_value,
                            job_code=job_code,
                            target_code=target.target_code)

            db.session.add(new_label)

        db.session.commit()

        flash("Target and labels successfully added!", "success")
        return redirect(url_for("targets"))

    elif request.method == "GET":
        return render_template(
                "target.html",
                job=job,
                labels=labels,
                title=f"Add Targets - {job.job_name}",)

@app.route("/target/<int:target_code>/update", methods=["GET", "POST"])
@login_required
def update_target(target_code :int):
    """

    """

    target = Target.query.get_or_404(target_code)
    labels = Label.query.filter_by(
                        target_code=target_code,
                        status=1,
                        deleted=0).all()

    if request.method == "POST":
        target_name = request.form["target_name"]
        check_exists = Target.query.filter_by(
                            target_name=target_name,
                            job_code=target.job_code,
                            status=1,
                            deleted=0).all()

        if check_exists and target_name != target.target_name:

            flash(f"Target '{target_name}' already exists!", "warning")
            return redirect(url_for("update_target", target_code=target_code))

        target.target_name = target_name
        db.session.commit()

        form_data = dict(request.form)
        
        for label in labels:

            current_label = Label.query.filter_by(
                                label_key=label.label_key,
                                target_code=target_code,
                                status=1,
                                deleted=0).first()

            label_value = form_data.get(label.label_key)

            current_label.label_value = label_value
            db.session.commit()

        flash("Target successfuly updated.", "success")
        return redirect(url_for("update_target", target_code=target_code))

    return render_template(
        "update_target.html",
        title="Update Target",
        target=target,
        labels=labels)

@app.route("/target/<int:target_code>/delete", methods=["GET", "POST"])
@login_required
def delete_target(target_code: int):
    """

    """

    target = Target.query.get_or_404(target_code)

    if request.method == "POST":
        target.status = 0
        target.deleted = 1

        for label in target.labels:
            label.status = 0
            label.deleted = 1

        db.session.commit()

        flash("Target has been successfully deleted!", "danger")
        return redirect(url_for("index"))

    target.status = 0
    for label in target.labels:
        label.status = 0

    db.session.commit()

    flash("Target has been successfully deactivated!", "warning")
    return redirect(url_for("index"))

@app.route("/job/<int:job_code>/update", methods=["GET", "POST"])
@login_required
def update_job(job_code :int):
    """

    """

    job = Job.query.get_or_404(job_code)
    labels = JobLabel.query.filter_by(
                            job_code=job_code,
                            status=1,
                            deleted=0).all()
    targets = Target.query.filter_by(
                            job_code=job_code,
                            status=1,
                            deleted=0).all()
    exporters = Exporter.query.filter_by(status=1, deleted=0).all()

    if request.method == "POST":

        scrape = request.form["scrape"]
        job_name = request.form["job_name"]
        exporter = request.form["exporter"]

        check_exists = Job.query.filter_by(
                            job_name=job_name,
                            status=1,
                            deleted=0).all()

        if check_exists and job_name != job.job_name:
            flash(f"Job '{job_name}' already exists!", "danger")
            return redirect(url_for("update_job", job_code=job_code))

        job.job_name = job_name
        job.scrape_interval = scrape
        job.exporter_code = exporter

        db.session.commit()

        flash("Job has been successfully updated.", "warning")
        return redirect(url_for("update_job", job_code=job_code))

    return render_template(
        "update_job.html",
        job=job,
        labels=labels,
        targets=targets,
        title="Update Job",
        exporters=exporters,
    )

@app.route("/job/<int:job_code>/delete", methods=["GET", "POST"])
@login_required
def delete_job(job_code :int):
    """

    """

    job = Job.query.get_or_404(job_code)

    if request.method == "POST":
        job.status = 0
        job.deleted = 1

        for target in job.targets:
            target.status = 0
            target.deleted = 1
        for label in job.labels:
            label.status = 0
            label.deleted = 1

        db.session.commit()

        flash("Job has been successfully deleted!", "danger")
        return redirect(url_for("jobs"))

    job.status = 0
    for target in job.targets:
        target.status = 0
    for label in job.labels:
        label.status = 0

    db.session.commit()

    flash("Job has been successfully deactivated.", "warning")
    return redirect(url_for("jobs"))

@app.route("/refresh", methods=["POST"])
@login_required
def refresh():

    configs = {}

    default_configs = {
        "global": {
            "scrape_interval": "15s", 
            "evaluation_interval": "15s"
        },

        "rule_files": [
            "alert.osho1.rules.yml"
        ],

        "alerting": 
            {
                "alertmanagers": 
                    [
                        {
                            "static_configs": [
                                {
                                    "targets": ["127.0.0.1:9093"]
                                }
                            ]
                        }
                    ]
        },

        "scrape_configs": [
            {
                "job_name": "prometheus",
                "static_configs": [
                    {"targets": ["127.0.0.1:9090"]}
                ]
            }

        ]
    }

    configs.update(default_configs)
    all_configs = []

    if request.method == "POST":
        jobs = Job.query.filter_by(status=1).all()

        for job in jobs:

            job_name = job.job_name
            relabel_port = job.exporter.relabel_port
            job_exporter = job.exporter.exporter_name
            scrape_interval = f"{job.scrape_interval}s"

            job_targets = job.targets
            job_labels = job.labels

            job_config = {
                "job_name": job_name,
                "job_labels": job_labels,
                "job_targets": job_targets,
                "job_exporter": job_exporter,
                "relabel_port": relabel_port,
                "scrape_interval": scrape_interval,
            }

            if job.exporter.exporter_metric_path:
                metrics_path = job.exporter.exporter_metric_path
 
                job_config.update(metrics_path=metrics_path)

            if job.exporter.exporter_module:
                module = job.exporter.exporter_module

                job_config.update(module=module)

            all_configs.append(job_config)

        for job in all_configs:

            current_config = {
                "job_name": job["job_name"],
                "scrape_interval": job["scrape_interval"],
            }

            if "metrics_path" in job:
                metrics_path = f"/{job['metrics_path']}"

                current_config.update(metrics_path=metrics_path)

            if "module" in job:
                curr_jb = Job.query.filter_by(
                            job_name=job["job_name"],
                            status=1,
                            deleted=0).first()

                module = curr_jb.exporter.exporter_module

                params = {
                    "module": [str(module)]
                }

                current_config.update(params=params)

            current_config.update(static_configs=[])

            for target in job["job_targets"]:

                target_config = {
                    "targets": [target.target_name],
                    "labels": {},
                }

                for label in target.labels:

                    key = label.label_key
                    value = label.label_value

                    curr_label = { key: value }

                    target_config["labels"].update(curr_label)

                current_config["static_configs"].append(target_config)

                relabel_configs = [
                        {
                            "source_labels": ["__address__"], 
                            "target_label": "__param_target"
                        }, 
                        {
                            "source_labels": ["__param_target"], 
                            "target_label": "instance"
                        }, 
                        {
                            "target_label": "__address__", 
                            "replacement": f"127.0.0.1:{job['relabel_port']}"
                        }
                ]

                current_config.update(relabel_configs=relabel_configs)
            
            configs["scrape_configs"].append(current_config)

    with open("prometheus.yml", "w") as f:
        yaml.dump(configs, f, sort_keys=False)

    flash("Server successfully refreshed!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

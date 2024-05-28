#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trie.ari.lt"""

import os
import subprocess as sp
import time
import typing as t
from base64 import urlsafe_b64encode
from warnings import filterwarnings as filter_warnings

import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wrappers import Response

app: flask.Flask = flask.Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore

app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["SECRET_KEY"] = os.urandom(1024 * 16)

app.config["SESSION_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["USE_SESSION_FOR_NEXT"] = True

MIN_LENGTH_MAX: t.Final[int] = 256
COUNT_MAX: t.Final[int] = 128
MAX_TEXT: t.Final[int] = 2**14  # 16 KB
MAX_FILESIZE: t.Final[int] = 2**32  # 4 GB

limit: Limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "1500 per hour", "30 per minute", "6 per second"],
    storage_uri="memcached://127.0.0.1:15391",
)


@app.context_processor  # type: ignore
def context() -> t.Dict[str, t.Any]:
    """expose constants"""

    return {
        "minlen": MIN_LENGTH_MAX,
        "sentcnt": COUNT_MAX,
        "maxtext": MAX_TEXT,
        "filesize": MAX_FILESIZE,
    }


@app.get("/")
def index() -> str:
    return flask.render_template("index.j2")


@app.post("/")
@limit.limit("1 per 1 minute")
def update():
    while os.path.exists("model.lock"):
        time.sleep(1)

    open("model.lock", "w").close()

    if os.path.getsize("model.bin") >= MAX_FILESIZE:
        flask.abort(413)

    if "text" not in flask.request.form:
        flask.abort(400)

    text: str = flask.request.form["text"][:MAX_TEXT].strip()

    if not text:
        flask.abort(400)

    process: sp.Popen[bytes] = sp.Popen(
        ("trie-update", "model.bin"), stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE
    )

    os.remove("model.lock")

    stdout, stderr = process.communicate(input=text.encode("utf-8", errors="ignore"))

    return flask.Response(
        f"""Done. Exit code: {process.wait()}

Stdout:

{stdout.decode("ascii", errors="ignore")}

Stderr:

{stderr.decode("ascii", errors="ignore")}

Text:

{text}""",
        mimetype="text/plain",
    )


@app.get("/robots.txt")
def robots() -> Response:
    return flask.redirect("https://ari.lt/robots.txt", 302)


@app.get("/favicon.ico")
def favicon() -> Response:
    return flask.redirect("https://ari.lt/favicon.ico", 302)


@app.get("/git")
def git() -> Response:
    return flask.redirect("https://ari.lt/lh/trie.ari.lt", 302)


@app.get("/gen/<path:seed>")
@app.get("/gen")
@app.get("/gen/")
def gen(seed: t.Optional[str] = None) -> t.Any:
    if not seed:
        seed = (
            urlsafe_b64encode(os.urandom(33)).decode("ascii")
            + "_"
            + str(round(time.time()))
        )

    m: int = int(flask.request.args.get("min", 16))
    c: int = int(flask.request.args.get("count", 8))

    if m > MIN_LENGTH_MAX or c > COUNT_MAX:
        flask.abort(400)

    r: flask.Response

    try:
        r = flask.Response(
            f"""Warning: This is public domain computer-generated text generated by https://ari.lt/lh/trie.ari.lt - anything said on this page has nothing to do with ari.lt. Licensed under the Unlicense (https://unlicense.org/).
Seed: {seed} (/gen/<seed> pattern apples to the URL, which isn't permanent and will redirect to other data with time as the model changes)

----- BEGIN LIBTRIE GENERATED TEXT -----
{sp.check_output(("trie-generate", "model.bin", seed, str(m), str(c))).decode("utf-8", errors="replace").strip()}
----- END LIBTRIE GENERATED TEXT -----""",
            mimetype="text/plain",
        )
    except Exception:
        r = flask.Response("Bad request.", mimetype="text/plain", status=400)

    r.headers["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    r.headers["Cache-Control"] = (
        "max-age=0, no-cache, must-revalidate, proxy-revalidate"
    )
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, HEAD"

    return r


if os.path.exists("model.lock"):
    os.remove("model.lock")


def main() -> int:
    """entry/main function"""

    app.run("127.0.0.1", 8080, True)

    return 0


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    raise SystemExit(main())

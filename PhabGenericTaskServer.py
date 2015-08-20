import phabricator, json
from datetime import datetime

from functools import wraps
from flask import request, Response, Flask, jsonify, request, make_response

from lib import config

app = Flask(__name__)
USER_PHIDS = {}


def check_auth(username, password):
    if len(username) > 5 and len(password) > 10:
        return True
    else:
        # False because we use user / api key in phabricator
        return False


def authenticate():
    """ Sends a 401 response that enables basic auth """

    return Response(
        "Auth required.\n"
        "You have to login with proper credentials", 401,
        { "WWW-Authenticate": "Basic realm=\"Login Required\"" }
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


class TaskSorter:
    def __init__(self, user_phid):
        self.user_phid = user_phid

    def compare(self, a, b):
        prio_values = {"High": 10, "Normal": 5, "Low": 1 }
        v_a = prio_values.get(a["priority"], 0)
        v_b = prio_values.get(b["priority"], 0)

        if self.user_phid == a["ownerPHID"]:
            v_a += 10
        if self.user_phid == b["ownerPHID"]:
            v_b += 10

        if v_a == v_b:
            v_a = int(a["dateModified"])
            v_b = int(b["dateModified"])

        return v_b - v_a


def transform_task(task):
    ret = {
        "id": task["objectName"],
        "summary": task["title"],
        "description": task["description"],
        "updated": datetime.fromtimestamp(int(task["dateModified"])).isoformat(),
        "created": datetime.fromtimestamp(int(task["dateCreated"])).isoformat(),
        "issueUrl": task["uri"],
        "closed": task["statusName"] == "Closed"
    }

    return ret


@app.route("/tasks")
@requires_auth
def user_tasks():
    username = request.authorization.username
    password = request.authorization.password

    phab = phabricator.Phabricator(username = username, certificate = password, host = config.PHAB_API_URL)

    if USER_PHIDS.has_key(username):
        user_phid = USER_PHIDS.get(username)
    else:
        ret = phab.user.query(usernames = [ username ])
        user_phid = ret[0]["phid"]
        USER_PHIDS[username] = user_phid

    limit = config.TASKS_LIMIT

    m = {}
    tasks = []

    ret = phab.maniphest.query(ownerPHIDs = [ user_phid ], status = "status-open", limit = limit, order = "order-priority")
    for task_phid in ret:
        m[task_phid] = True
        task = ret[task_phid]
        tasks.append(task)

    limit = min(limit, limit - len(tasks))
    # uncomment if you only want tasks assigned to you without the ones you're just CC
    # limit = 0
    if limit > 0:
        ret = phab.maniphest.query(ccPHIDs = [ user_phid ], status = "status-open", limit = limit, order = "order-priority")
        for task_phid in ret:
            if m.has_key(task_phid):
                continue
            task = ret[task_phid]
            tasks.append(task)

    t = TaskSorter(user_phid)
    tasks.sort(cmp = t.compare)

    new_tasks = []

    for t in tasks:
        t = transform_task(t)
        new_tasks.append(t)

    tasks = {"tasks": new_tasks }

    ret = make_response(json.dumps(tasks))
    ret.headers["Content-Type"] = "text/json; charset=UTF-8"
    return ret

@app.route("/task/<id>")
@requires_auth
def load_task(id):
    username = request.authorization.username
    password = request.authorization.password

    phab = phabricator.Phabricator(username = username, certificate = password, host = config.PHAB_API_URL)
    ret = phab.maniphest.query(ids = [ id.replace("T", "") ])
    t = transform_task(ret.response.values()[0])
    t = { "task": t }

    ret = make_response(json.dumps(t))
    ret.headers["Content-Type"] = "text/json; charset=UTF-8"
    return ret

if __name__ == '__main__':
    app.run()

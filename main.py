from celery import Celery, Task, shared_task
from flask import Flask, request
from celery.result import AsyncResult
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app



app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379",
        result_backend="redis://localhost:6379",
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)

# def create_app() -> Flask:
#     app = Flask(__name__)
#     app.config.from_mapping(
#         CELERY=dict(
#             broker_url="redis://localhost:6379",
#             result_backend="redis://localhost:6379",
#             task_ignore_result=True,
#         ),
#     )
#     app.config.from_prefixed_env()
#     celery_init_app(app)
#     return app




@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b



@app.get("/add")
def start_add():
    print(request.args)
    a = int(request.args.get("a"))
    b = int(request.args.get("b"))
    result = add_together.delay(a, b)
    return {"result_id": result.id}



@app.get("/result/<id>")
def task_result(id):
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
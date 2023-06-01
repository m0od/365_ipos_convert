from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    from project.users import users_router                # new
    app.include_router(users_router)                      # new

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app

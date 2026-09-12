from fastapi import FastAPI
from UseModel import router as Pred_router


def create_app():
    app = FastAPI(title="Solar + Wind Power Prediction API")
    app.include_router(Pred_router)


    return app
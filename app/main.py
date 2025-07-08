from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users

app = FastAPI(
    title="KYC Microservice",
    description="Microservicio para registro de usuarios con validación KYC",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["users"])


@app.get("/")
async def root():
    return {"message": "KYC Microservice API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kyc-microservice"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)

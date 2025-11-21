import strawberry
from fastapi import FastAPI
from typing import List
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from pymongo import MongoClient
from bson.objectid import ObjectId

# -----------------------------
# MongoDB 연결 설정
# -----------------------------
mongo = MongoClient("mongodb://localhost:27017")
db = mongo["employee_db"]
collection = db["employees"]


# -----------------------------
# GraphQL 타입
# -----------------------------
@strawberry.type
class Employee:
    id: strawberry.ID
    name: str
    age: int
    job: str
    language: str
    pay: int


@strawberry.input
class EmployeeInput:
    name: str
    age: int
    job: str
    language: str
    pay: int


# MongoDB → GraphQL 변환
def mongo_to_graphql(doc) -> Employee:
    return Employee(
        id=str(doc["_id"]),
        name=doc["name"],
        age=doc["age"],
        job=doc["job"],
        language=doc["language"],
        pay=doc["pay"],
    )


# -----------------------------
# Query
# -----------------------------
@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[Employee]:
        docs = list(collection.find())
        return [mongo_to_graphql(doc) for doc in docs]


# -----------------------------
# Mutation
# -----------------------------
@strawberry.type
class Mutation:
    @strawberry.mutation
    def createEmployee(self, input: EmployeeInput) -> Employee:
        data = {
            "name": input.name,
            "age": input.age,
            "job": input.job,
            "language": input.language,
            "pay": input.pay,
        }
        result = collection.insert_one(data)
        data["_id"] = result.inserted_id
        return mongo_to_graphql(data)

    @strawberry.mutation
    def updateEmployee(self, id: strawberry.ID, input: EmployeeInput) -> Employee:
        oid = ObjectId(id)
        update_data = {
            "name": input.name,
            "age": input.age,
            "job": input.job,
            "language": input.language,
            "pay": input.pay,
        }

        collection.update_one({"_id": oid}, {"$set": update_data})
        updated = collection.find_one({"_id": oid})

        if not updated:
            raise ValueError("Employee not found")

        return mongo_to_graphql(updated)

    @strawberry.mutation
    def deleteEmployee(self, id: strawberry.ID) -> strawberry.ID:
        oid = ObjectId(id)
        collection.delete_one({"_id": oid})
        return id


# -----------------------------
# FastAPI + GraphQL 세팅
# -----------------------------
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()


@app.on_event("startup")
def startup_event():
    # 기본 샘플 데이터가 없으면 넣기
    if collection.count_documents({}) == 0:
        samples = [
            {"name": "John", "age": 35, "job": "frontend", "language": "react", "pay": 400},
            {"name": "Peter", "age": 28, "job": "backend", "language": "java", "pay": 300},
            {"name": "Sue", "age": 38, "job": "publisher", "language": "javascript", "pay": 400},
            {"name": "Susan", "age": 45, "job": "pm", "language": "python", "pay": 500},
        ]
        collection.insert_many(samples)


# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "FastAPI GraphQL MongoDB Employee 서버 동작 중!"}

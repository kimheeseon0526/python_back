import strawberry
from typing import Optional, List
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from db.database import Base, Session as SessionLocal, engine
from db.models import EmployeeModel


@strawberry.type
class Employee:
    id: strawberry.ID
    name: str
    age: int
    job: str
    language:str
    pay: int

@strawberry.input
class EmployeeInput:
    name: str
    age: int
    job: str
    language: str
    pay: int

# ORM 객체 -> GraphQL 타입 변환 도움미
def orm_to_graphql(emp: EmployeeModel) -> Employee:
    return Employee(
        id = str(emp.id),
        name = emp.name,
        age= emp.age,
        job= emp.job,
        language = emp.language,
        pay = emp.pay
    )

@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[Employee]:
        with SessionLocal() as db:
            rows =db.query(EmployeeModel).all()
            return [orm_to_graphql(row) for row in rows]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def createEmployee(self, input: EmployeeInput) -> Employee:
        # 등록 쿼리
        with SessionLocal() as db:
            new_emp = EmployeeModel(
                name=input.name,
                age=input.age,
                job=input.job,
                language=input.language,
                pay=input.pay
            )
            db.add(new_emp)
            db.commit()
            db.refresh(new_emp)
            return orm_to_graphql(new_emp)


    @strawberry.mutation
    def updateEmployee(self, id:strawberry.ID, input: EmployeeInput) -> Employee:
        # 수정 쿼리
        emp_id = int(id)
        with SessionLocal() as db:
            row = db.query(EmployeeModel).filter(EmployeeModel.id == emp_id).first()
            if row is None:
                raise ValueError("Employee not found")

            row.name=input.name,
            row.age=input.age,
            row.job=input.job,
            row.language=input.language,
            row.pay=input.pay

            db.commit()
            db.refresh(row)
            return orm_to_graphql(row)

    @strawberry.mutation
    def deleteEmployee(self, id:strawberry.ID) -> strawberry.ID:
        print("id" , id)
        emp_id = int(id)
        with SessionLocal() as db:
            row = db.query(EmployeeModel).filter(EmployeeModel.id == emp_id).first()
            if row is None:
                raise ValueError("Employee not found")
            db.delete(row)
            db.commit()
            return emp_id


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

def init_sample_data():
    """서버 최초 실행 시 샘플 직원 데이터 넣기 (이미 있으면 스킵)"""
    from sqlalchemy.exc import IntegrityError

    with SessionLocal() as db:
        # 이미 데이터가 있으면 초기화 X
        if db.query(EmployeeModel).count() > 0:
            return

        samples = [
            EmployeeModel(name="John",  age=35, job="frontend",  language="react",      pay=400),
            EmployeeModel(name="Peter", age=28, job="backend",   language="java",       pay=300),
            EmployeeModel(name="Sue",   age=38, job="publisher", language="javascript", pay=400),
            EmployeeModel(name="Susan", age=45, job="pm",        language="python",     pay=500),
        ]

        db.add_all(samples)
        db.commit()



app = FastAPI()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    init_sample_data()

# CORS 설정
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
    return {"message": "FastAPI GraphQL Employee 서버 동작 중....."}







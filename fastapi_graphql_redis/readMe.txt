pip install -r requirements.txt

#서버 실행(docker 사용시에는 docker 실행 후 서버 실행 시켜야함)
uvicorn main:app --reload --port 3001


Query 쿼리
query {
  employees {
    id
    name
    age
    job
    language
    pay
  }
}

Mutaion 쿼리

post 방식
mutation {
  createEmployee(
    input: {
      name: "Taylor"
      age: 29
      job: "backend"
      language: "python"
      pay: 410
    }
  ) {
    id
    name
    age
    job
    language
    pay
  }
}

put 방식
mutation {
  updateEmployee(
    id: "2"
    input: {
      name: "Peter"
      age: 30
      job: "backend"
      language: "java"
      pay: 350
    }
  ) {
    id
    name
    age
    job
    language
    pay
  }
}

delete 방식
mutation {
  deleteEmployee(id: "3")
}



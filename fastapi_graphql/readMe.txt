pip install -r requirements.txt

#서버 실행 명령문
uvicorn main:app --reload --port 3001

#쿼리문
Query
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

#Mutation 쿼리
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

#put 방식(수정)
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

#삭제
delete
mutation {
  deleteEmployee(id: "3")
}
from pydantic import BaseModel

class CatFact(BaseModel):
    fact: str
    length: int

class GitHubUser(BaseModel):
    login: str
    public_repos: int
    followers: int
    name: str | None

class AgeGuess(BaseModel):
    count: int
    name: str
    age: int | None



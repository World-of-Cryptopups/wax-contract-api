from typing import Any, Dict, List
from aioeos import EosAccount, EosAction, EosPermissionLevel
from fastapi import FastAPI
from pydantic import BaseModel
from wax import WaxHandler

app = FastAPI()


@app.get("/")
def main():
    return "Wax Contract API v0.1.0"


class Authorization(BaseModel):
    actor: str
    permission: str


class Account(BaseModel):
    name: str
    private_key: str


class Action(BaseModel):
    account: str
    name: str
    authorization: List[Authorization]
    data: Dict[str, Any]


class TransactBody(BaseModel):
    account: Account
    action: Action
    endpoints: List[str]


@app.post("/transact")
async def transact(transact: TransactBody):
    # account
    account = EosAccount(
        name=transact.account.name, private_key=transact.account.private_key
    )

    # setup transact
    authorization = []
    for i in transact.action.authorization:
        authorization.append(EosPermissionLevel(actor=i.actor, permission=i.permission))

    action = EosAction(
        account=transact.action.account,
        name=transact.action.name,
        authorization=authorization,
        data=transact.action.data,
    )

    client = WaxHandler(account, transact.endpoints)

    # call
    try:
        transact = await client.transact(action)
    except Exception as e:
        return {"error": e.__str__()}

    return transact

from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request
import requests, time # for sending request to another microservice
from fastapi.background import BackgroundTasks

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=['*'],
    allow_methods=['*'],
)


# this should be another database
redis = get_redis_connection(
    host="redis-12348.crce179.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12348,
    password="vFlD3wrdn4CEOrbSlaDiRjRB4Cu2BLHi",
    decode_responses=True,

)


class Order(HashModel):
    product_id : str
    fee : float
    total : float
    status : str # pending, completed, refunded
    price: float
    quantity: int

    class Meta:
        database = redis


class OrderRequest(BaseModel):
    product_id : str
    fee : float
    total : float
    status : str
    price: float
    quantity: int


# def format(pk : str):
#     product = Order.get(pk)

#     return {
#         "id": product.pk,
#         "name": product.name,
#         "price": product.price,
#         "quantity": product.quantity
#     }


# @app.get("/products")
# async def products():
#     return [format(pk) for pk in Order.all_pks()]


# @app.post("/products")
# def create_product(product: OrderRequest):
#     new_product = Order(**product.model_dump())
#     new_product.save()
#     return new_product



# @app.get("/product/{pk}")
# def getOne(pk : str):
#     return Order.get(pk)



# @app.delete("/product/{pk}")
# def deleteProduct(pk : str):
#     return Order.delete(pk)


@app.get("/order/{pk}")
def getOrder(pk : str):
    return Order.get(pk)




@app.post("/order")
async def getOrder(request : Request, background_tasks: BackgroundTasks):
    body = await request.json() # id, quantity

    req = requests.get("http://127.0.0.1:8000/product/%s" % body["id"])
    product = req.json()

    order = Order(
        product_id = body["id"],
        price = product["price"],
        fee = 0.2 * product["price"],
        total = product["price"] * 1.2,
        status = "pending",
        quantity = body["quantity"]
    )

    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd('order_completed', order.model_dump(), '*') # sends an event, create consumer in the other microservice

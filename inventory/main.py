from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=['*'],
    allow_methods=['*'],
)
redis = get_redis_connection(
    host="redis-12348.crce179.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12348,
    password="vFlD3wrdn4CEOrbSlaDiRjRB4Cu2BLHi",
    decode_responses=True,

)


class Product(HashModel):
    name : str
    price: float
    quantity: int

    class Meta:
        database = redis


class ProductRequest(BaseModel):
    name: str
    price: float
    quantity: int


def format(pk : str):
    product = Product.get(pk)

    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.get("/products")
async def products():
    return [format(pk) for pk in Product.all_pks()]


@app.post("/products")
def create_product(product: ProductRequest):
    new_product = Product(**product.model_dump())
    new_product.save()
    return new_product



@app.get("/product/{pk}")
def getOne(pk : str):
    return Product.get(pk)



@app.delete("/product/{pk}")
def deleteProduct(pk : str):
    return Product.delete(pk)
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)

items = [
    # {
    #     "id": 1,
    #     "title": "Book 1",
    #     "description": "Book 1 description",
    #     "category": "Book",
    #     "price": 100.0,
    #     "discount": None,
    #     "quantity": 10
    # },
    # {
    #     "id": 2,
    #     "title": "Book 2",
    #     "description": "Book 2 description",
    #     "category": "Book",
    #     "price": 200.0,
    #     "discount": 10.0,
    #     "quantity": 5
    # },
    # {
    #     "id": 3,
    #     "title": "Magazine 1",
    #     "description": "Magazine 1 description",
    #     "category": "Magazine",
    #     "price": 300.0,
    #     "discount": None,
    #     "quantity": 20
    # }
]


class ItemBase(BaseModel):
    title: str
    description: str
    category: str
    price: float
    discount: float | None
    quantity: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

class SaleResponse(BaseModel):
    message: str
    items: List[Item]
class IncrementResponse(BaseModel):
    items: List[Item]
@app.get('/items', response_model=List[Item])
def get_items():
    return items

@app.get('/items/{id}', response_model=Item)
def get_item_by_id(id: int):
    for item in items:
        if item['id'] == id:
            return item
    raise HTTPException(404, 'Item not found')

@app.post('/items', response_model=Item)
def create_item(item: ItemCreate):
    if len(items) == 0:
        item = Item(id = 1, **item.model_dump()).model_dump()
    else:
        item = Item(id = items[-1]['id'] + 1, **item.model_dump()).model_dump()
    items.append(item)
    return item

@app.put('/items/{id}', response_model=Item)
def change_item(id: int, upd_item: ItemCreate):
    for item in items:
        if item['id'] == id:
            for k, v in upd_item.model_dump().items():
                item[k] = v
            return item
    raise HTTPException(404, 'Item not found')

@app.delete('/items/{id}')
def delete_item(id: int):
    for item in items:
        if item['id'] == id:
            items.remove(item)
            return {"message": "Item deleted"}
    raise HTTPException(404, 'Item not found')

@app.get('/items/filter/', response_model=SaleResponse)
def filter_items(title: str | None = None,
                 description: str | None = None,
                 category: str | None = None,
                 price_from: float | None = None,
                 price_to: float | None = None,
                 discount_from: float | None = None,
                 discount_to: float | None = None,
                 quantity_from: float | None = None,
                 quantity_to: float | None = None):
    filtered_items = []
    for item in items:
        if (
            (not title or title.lower() in item['title'].lower())
            and (not description or description.lower() in item['description'].lower())
            and (not category or category.lower() == item['category'].lower())
            and (not price_from or price_from <= item['price'])
            and (not price_to or price_to >= item['price'])
            and (not discount_from or discount_from <= item['discount'])
            and (not discount_to or discount_to >= item['discount'])
            and (not quantity_from or quantity_from <= item['quantity'])
            and (not quantity_to or quantity_to >= item['quantity'])
        ):
            filtered_items.append(item)
    return filtered_items

    
@app.get('/sale/{id}', response_model=SaleResponse)
def sell_item(id: str):
    id_list = [int(item_id) for item_id in id.split(',')]
    sold_items = []
    for item_id in id_list:
        for item in items:
            if item['id'] == item_id:
                if item['quantity'] > 0:
                    item['quantity'] -= 1
                    sold_items.append(item)
                else:
                    raise HTTPException(404, 'Item not found')
    if len(sold_items) > 0:
        return {'message': 'Items sold', 'items': sold_items}
    else:
        raise HTTPException(404, 'Item not found')

@app.get('/increment/{id}{quantity}', response_model=IncrementResponse)
def increment_items(id: str, quantity: str):
    id_list = [int(item_id) for item_id in id.split(',')]
    quantity_list = [int(item_quantity) for item_quantity in quantity.split(',')]
    if len(id_list) != len(quantity_list):
        raise HTTPException(404, 'Item not found')
    for i in range(len(id_list)):
        for item in items:
            if item['id'] == id_list[i]:
                    item['quantity'] += quantity_list[i]
                    break
    return {'items': items}

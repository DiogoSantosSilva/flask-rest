from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field canot be left blank!"
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id."
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item  with name '{}' already exists".format(name)}, 400

        data = Item.parser.parse_args()
        
        item = ItemModel(name, data['price'], data['store_id']) #or ItemModel(name, **data)

        try:
            item.save_to_db()
        except Exception as error:
            return {'message': 'An error occurred, {}'.format( error)}, 500 

        return item.json(), 201
    
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message':'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            try:
                item = ItemModel(name, data['price'], data['store_id'])
            except Exception as error:
                return {'message': "Error to insert item '{}', {} ".format(updated_item['name'], error)}, 500
        else:
            try:
                item.price = data['price']
            except Exception as error:
                return {'message': "Error to update item '{}', {} ".format(updated_item['name'], error)}, 500

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.query.all()]}
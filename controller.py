
from db import Database


class Item:
    db = Database()

    def __init__(self, **kwargs):
        self.data = {key.lower(): value for (key, value) in kwargs.items()}

    @property
    def name(self):
        return self.data.get('item_name').capitalize()
    
    @property
    def quantity(self):
        value = self.data.get('quantity')
        if not value:
            value = 0
        return str(value)

    @quantity.setter
    def quantity(self, quantity):
        if not quantity:
            quantity = 0
        else:
            quantity = int(quantity)
        self.db.update_item(self.name, quantity=quantity)
        self.data['quantity'] = quantity

    @property
    def amount(self):
        return str(self.data.get('amount', 0))

    @amount.setter
    def amount(self, amount):
        if not amount:
            amount = 0
        else:
            amount = int(amount)
        self.db.update_item(self.name, amount=amount)
        self.data['amount'] = amount

    @property
    def category(self):
        return self.data.get('category_name', '') or ''

    @category.setter
    def category(self, category):
        print('UPDATING CATEGORY IN CONTROLLER:', category)
        self.db.update_item(self.name, category=category)
        self.data['category_name'] = category

    @property
    def common(self):
        return bool(self.data.get('common', 0))

    @common.setter
    def common(self, common):
        common = int(common)
        self.db.update_item(self.name, common=common)
        self.data['common'] = common



class Controller:
    db = Database() 

    def __init__(self):
        pass
        # self._init_database()

    # def _init_database(self):
    #     self.db = Database()

    def add_unit(self, name):
        self.db.add_unit(name)

    def add_category(self, name):
        self.db.add_category(name)
    
    def add_item(self, **kwargs):
        print('- ADDING ITEMS')
        data = {}
        for key, value in kwargs.items():
            if type(value) == str:
                value = value.lower()
            data[key] = value
        self.db.add_item(**data)

    def delete_unit(self, name):
        self.db.delete_unit(name)

    def delete_category(self, name):
        self.db.delete_category(name)

    def delete_item(self, name):
        self.db.delete_item(name)
        
    def get_unit_list(self):
        return self._capitalized_list(self.db.get_unit_list())

    def get_category_list(self):
        return self._capitalized_list(self.db.get_category_list())

    def get_item_list(self, unit):
        return self._capitalized_list(self.db.get_item_list(unit))

    def get_items(self, unit_name=None, category_name=None):
        if unit_name:
            unit_name = unit_name.lower()
        if category_name:
            category_name = category_name.lower()
        data = self.db.get_item_data(unit_name=unit_name, 
                                     category_name=category_name)
        return_dict = {}
        print(data)
        for item in data:
            # key = f'{unit}_{item["item_name"]}'
            key = f'{item["unit_name"]}_{item["item_name"]}'
            return_dict[key] = Item(**item)
        return return_dict

    def update_item(self, name, **kwargs):
        self.db.update_item(name, **kwargs)

    def _capitalized_list(self, lst):
        return [item.capitalize() for item in lst]


if __name__ == '__main__':
    c = Controller()
    print(c.get_item_list('skap1'))
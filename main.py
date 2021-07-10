
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.toast import toast

from controller import Controller

# from sqlite3 import IntegrityError

import exceptions


class OkCancelPopup(Popup):
    container = ObjectProperty()
    buttons = ObjectProperty()
    button_ok_color = ListProperty([0, 1, 0, .5])
    button_cancel_color = ListProperty([1, 0, 0, .5])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._callback_ok = set()
        self._callback_cancel = set()

    def add_callback_ok(self, func):
        self._callback_ok.add(func)

    def add_callback_cancel(self, func):
        self._callback_cancel.add(func)
    
    def _on_ok(self):
        for func in self._callback_ok:
            func()

    def _on_cancel(self):
        if not self._callback_cancel:
            self.dismiss()
            return
        for func in self._callback_cancel:
            func()


class ItemWidget(BoxLayout):
    name = ObjectProperty()
    category = ObjectProperty
    quantity = ObjectProperty()
    amount = ObjectProperty()
    common = ObjectProperty

    def on_change_quantity(self):
        quantity = ''.join([s for s in list(self.quantity.text) if s.isdigit()])
        self.quantity.text = quantity

    def on_reduce_quantity(self):
        q = int(self.quantity.text)
        q -= 1
        if q < 0:
            return
        self.quantity.text = str(q)
        app = MDApp.get_running_app()
        app.update_item(self)

    def on_increase_quantity(self):
        q = int(self.quantity.text)
        q += 1
        self.quantity.text = str(q)
        app = MDApp.get_running_app()
        app.update_item(self)

    def on_change_amount(self):
        amount = ''.join([s for s in list(self.amount.text) if s.isdigit()])
        self.amount.text = amount


# class ItemWidgetAdd(BoxLayout):
#     name = StringProperty()
#     number = StringProperty()

class UnitWidgetAdd(BoxLayout):
    name = ObjectProperty()

class CategoryWidgetAdd(BoxLayout):
    name = ObjectProperty()

class ItemWidgetAdd(BoxLayout):
    name = ObjectProperty()
    unit = ObjectProperty()
    category = ObjectProperty()
    quantity = ObjectProperty()
    amount = ObjectProperty()
    common = ObjectProperty

class ContentNavigationDrawer(BoxLayout):
    pass


class UnitDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))

class CategoryDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class ItemList(ThemableBehavior, MDList): 
    pass


class UnitList(ThemableBehavior, MDList):

    def on_select_unit_drawer(self, instance_item):
        app = MDApp.get_running_app()
        if instance_item.icon == 'plus':
            app.add_unit()
        else:
            app.on_select_unit(instance_item.text)

    # def _set_color_item(self, instance_item):
    #     """Called when tap on a menu item."""

    #     # Set the color of the icon and text for the menu item.
    #     for item in self.children:
    #         if item.text_color == self.theme_cls.primary_color:
    #             item.text_color = self.theme_cls.text_color
    #             break
    #     instance_item.text_color = self.theme_cls.primary_color


class CategoryList(ThemableBehavior, MDList):

    def on_select_category_drawer(self, instance_item):
        app = MDApp.get_running_app()
        if instance_item.icon == 'plus':
            app.add_category()
        else:
            app.on_select_category(instance_item.text)


class MainApp(MDApp):
    unit_widgets = {}
    item_widgets = {}
    category_widgets = {}
    current_unit = None
    current_category = None
    controller = Controller()
    items = {}
    add_unit_widget = None
    add_category_widget = None
    add_item_widget = None

    def on_start(self):
        self.update_drawer_lists()
        # icons_item = {
        #     "folder": "My files",
        #     "plus": "Lagg till plats",
        #     "account-multiple": "Shared with me",
        #     "star": "Starred",
        #     "history": "Recent",
        #     "checkbox-marked": "Shared with me",
        #     "upload": "Upload",
        # }
        # for icon_name in icons_item.keys():
        #     self.root.ids.content_drawer.ids.md_list.add_widget(
        #         ItemDrawer(icon='fridge', text=icons_item[icon_name])
        #     )

    @property
    def nav_drawer(self):
        return self.root.ids.nav_drawer

    @property
    def unit_list(self):
        return self.root.ids.content_drawer.ids.unit_list

    @property
    def category_list(self):
        return self.root.ids.content_drawer.ids.category_list

    @property
    def item_list(self):
        return self.root.ids.item_list

    @property
    def item_title(self):
        return self.root.ids.title

    def _reset_item_list(self):
        for item, wid in self.item_widgets.items():
            self.item_list.remove_widget(wid)
        self.item_widgets = {}
        self.current_category = None
        self.current_unit = None

    def _reset_unit_list(self):
        for unit, wid in self.unit_widgets.items():
            self.unit_list.remove_widget(wid)
        self.unit_widgets = {}

    def _reset_category_list(self):
        for category, wid in self.category_widgets.items():
            self.category_list.remove_widget(wid)
        self.category_widgets = {}

    def update_drawer_lists(self):
        print('- UPDATEING DRAWER LISTS')
        self._update_unit_list()
        self._update_category_list()

    def _update_unit_list(self):
        self._reset_unit_list()
        self._set_unit_list()

    def _update_category_list(self):
        self._reset_category_list()
        self._set_category_list()

    def _set_unit_list(self):
        unit_list = self.controller.get_unit_list()
        for unit in sorted(unit_list):
            wid = UnitDrawer(icon='fridge', text=unit)
            self.unit_list.add_widget(wid)
            self.unit_widgets[unit] = wid

    def _set_category_list(self):
        category_list = self.controller.get_category_list()
        for category in sorted(category_list):
            wid = CategoryDrawer(icon='alpha-c-circle-outline', text=category)
            self.category_list.add_widget(wid)
            self.category_widgets[category] = wid

    def add_unit(self): 
        print('Adding UNIT')
        self.add_unit_widget = UnitWidgetAdd()
        self.popup = OkCancelPopup()
        self.popup.size_hint_y = .3
        self.popup.buttons.size_hint_y = .5
        self.popup.title = f'Lägg till plats'
        self.popup.container.add_widget(self.add_unit_widget)
        self.popup.add_callback_ok(self._save_new_unit)
        self.popup.open()

    def _save_new_unit(self):
        name = self.add_unit_widget.name.text.strip()
        if name:
            try:
                self.controller.add_unit(name)
                self._update_unit_list()
            except exceptions.AlreadyInDatabase:
                toast(f'Platsen "{name}" finns redan')
            except Exception as e:
                toast('Något gick fel...')
        else:
            toast('Ingen ny plats angiven!')
        self.popup.dismiss()
        self.popup = None
        self.add_unit_widget = None

    def add_category(self):
        print('Adding CATEGORY')
        self.add_category_widget = CategoryWidgetAdd()
        self.popup = OkCancelPopup()
        self.popup.size_hint_y = .3
        self.popup.buttons.size_hint_y = .5
        self.popup.title = f'Lägg till kategori'
        self.popup.container.add_widget(self.add_category_widget)
        self.popup.add_callback_ok(self._save_new_category)
        self.popup.open()

    def _save_new_category(self):
        name = self.add_category_widget.name.text.strip()
        if name:
            try:
                self.controller.add_category(name)
                self._update_category_list()
            except exceptions.AlreadyInDatabase:
                toast(f'Kategorin "{name}" finns redan')
            except Exception as e:
                toast('Något gick fel...')
        else:
            toast('Ingen ny kategori angiven!')
        self.popup.dismiss()
        self.popup = None
        self.add_category_widget = None

    def add_item(self):
        print('ADD ITEM HERE')
        self.add_item_widget = ItemWidgetAdd()
        self.popup = OkCancelPopup()
        self.popup.size_hint_y = .9
        # self.popup.buttons.size_hint_y = .5
        self.popup.title = f'Lägg till vara'
        unit_list = self.controller.get_unit_list()
        category_list = [''] + self.controller.get_category_list()
        self.add_item_widget.unit.values = unit_list
        self.add_item_widget.category.values = category_list
        self.popup.container.add_widget(self.add_item_widget)
        self.popup.add_callback_ok(self._save_new_item)
        self.popup.open()

    def _save_new_item(self):
        item_name = self.add_item_widget.name.text
        unit_name = self.add_item_widget.unit.text
        category = self.add_item_widget.category.text
        quantity = self.add_item_widget.quantity.text
        amount = self.add_item_widget.amount.text
        common = self.add_item_widget.common.active
        data = dict(item_name=item_name, 
                    unit_name=unit_name, 
                    category=category, 
                    quantity=quantity, 
                    amount=amount, 
                    common=common)

        try:
            self.controller.add_item(**data)
            self.popup.dismiss()
            current_unit = self.current_unit
            current_category = self.current_category
            print('+++', current_unit, current_category)
            self.update_drawer_lists()
            if current_unit:
                self.on_select_unit(current_unit)
            elif current_category:
                self.on_select_category(current_category)
            toast(f'Varan {item_name.capitalize()} har lagts till på plats {unit_name.capitalize()}')
        except exceptions.MissingUnit:
            toast(f'Du måste ange plats!')
        except exceptions.AlreadyInDatabase:
            toast(f'Varan "{item_name}" finns redan')
            self.popup.dismiss()
        except Exception as e:
            toast('Något gick fel...')
            print(e)
            self.popup.dismiss()

    def on_select_unit(self, unit_name):
        if not unit_name:
            unit_name = self.current_unit
        print('- ON_SELECT_UNIT')
        unit_name = unit_name.lower()
        # self.current_unit = unit_name
        # self.current_category = None
        self.item_title.text = f'Plats: {unit_name.capitalize()}'
        self.update_item_list(unit_name=unit_name)
        self.nav_drawer.set_state(new_state='close')

    def on_select_category(self, category_name):
        if not category_name:
            category_name = self.current_category
        print('on_select_category')
        category_name = category_name.lower()
        # self.current_category = category_name
        # self.current_unit = None
        self.item_title.text = f'Kategori: {category_name.capitalize()}'
        self.update_item_list(category_name=category_name)
        self.nav_drawer.set_state(new_state='close')

    def update_item_list(self, unit_name=None, category_name=None):
        print('Updating item list with unit:', unit_name)
        print('Updating item list with category:', category_name)
        self._reset_item_list()
        if unit_name:
            # Clock.schedule_once(lambda x=unit_name: self._set_item_list_for_unit(x), 1)
            self._set_item_list_for_unit(unit_name)
        elif category_name:
            # Clock.schedule_once(lambda x=category_name: self._set_item_list_for_category(x), 1)
            self._set_item_list_for_category(category_name)

    def _set_item_list_for_unit(self, unit_name):
        print('_set_item_list_for_unit', unit_name)
        self.items = self.controller.get_items(unit_name=unit_name) 
        category_list = [''] + self.controller.get_category_list()
        self.current_unit = unit_name
        for key in sorted(self.items): 
            print('key', key)
            item = self.items[key]
            wid = ItemWidget()
            wid.category.values = category_list

            wid.name.text = item.name
            wid.quantity.text = item.quantity
            wid.amount.text = item.amount
            wid.common.active = item.common
            wid.category.text = item.category
            self.item_list.add_widget(wid)
            self.item_widgets[item.name] = wid

    def _set_item_list_for_category(self, category_name):
        pass

    def _item_key(self, item):
        if not self.current_unit:
            raise ValueError
        return f'{self.current_unit}_{item.lower()}'

    def update_item(self, item_widget):
        # print('=== item_widget', item_widget)
        # print('=== item_widget.name.text.lower()', item_widget.name.text.lower())
        # print('KEYS', list(self.items.keys()))
        item = self.items.get(self._item_key(item_widget.name.text))
        print('CAT', item_widget.category.text.lower())
        item.category = item_widget.category.text.lower()
        item.quantity = item_widget.quantity.text
        item.amount = item_widget.amount.text
        item.common = item_widget.common.active
        # self.controller.update_item(item_widget.name.text, 
        #                             number=item_widget.number.text, 
        #                             common=int(item_widget.common.active))
        print(item_widget.common.active)
        # print(item_widget)
        # print(item_widget.name.text, item_widget.number.text)

    def delete_item(self, item_widget):
        pass


MainApp().run()
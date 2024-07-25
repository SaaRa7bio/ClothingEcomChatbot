from idlelib import query

from bson import ObjectId

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
)

from telegram.ext import (
    CallbackContext,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
    ApplicationBuilder, Updater,
)

import logging
import asyncio
import os
from mongodb import collection, locations, reduce_availability, increment_availability
from datetime import datetime, timedelta



logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        # used the id to identify the collection because all other objects are porne to change
        self.id="dataset-id" #replace with a real dataset idea
        #these are the only people who are authorized to update the stock
        self.auth_users= ["username1", "username2", "username3"]
        #this group chat of the buisness where order details will be sent, it was required by the buisness manager
        self.GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID", "-4166632896")


    async def start(self, update: Update, context: CallbackContext):
        #a default welcome message
        with open('data\\defaultmsg.txt', 'r', encoding='utf-8') as file:
            welcome = file.read()

        keyboard = [
            [InlineKeyboardButton("Browse products", callback_data='purchase')],
            [InlineKeyboardButton("contact us", callback_data='customerService')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message(welcome, reply_markup=reply_markup)


    async def customer_service(self, update: Update, context: CallbackContext):
        #can be customized into more advanced cutomer service system but here we used simple phone number based on target audience
        query = update.callback_query
        await query.answer()

        await update.effective_chat.send_message("please call this number 07xxxxxx."
                                                 "\n \n please take into consideration the work time 9-5 pm")

    async def table(self, update: Update, context: CallbackContext):
        #body size check, can be improved into more complex interactive system that chooses the best size choice based on weight and height parameters (will work on this later)
        query = update.callback_query
        await query.answer()
        with open('data\\sizes.png', 'rb') as img_file:
            await update.effective_chat.send_photo(img_file)


    async def purchase(self, update: Update, context: CallbackContext):
        #displaying products categories
        query = update.callback_query # :)
        objInstance = ObjectId(self.id)
        doc_main = collection.find_one({"_id": objInstance})
        categories = doc_main.get("categories", [])
        cats = []

        counter = 1
        while True:
            key = f"cat{counter}"
            found_any = False
            for category in categories:
                if key in category:
                    cats.append(category[key])
                    found_any = True
            if not found_any:
                break
            counter += 1

        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"opt_cat{idx+1}_{cat}")] for idx, cat in enumerate(cats)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("choose a category", reply_markup=reply_markup)


    async def cat_opts(self, update: Update, context: CallbackContext):
        #retrieves user choice
        query = update.callback_query
        parts = query.data.split("_")

        cat = parts[1]
        category_value = parts[2]
        # stores user choices inside a dictionary
        context.user_data["selection"] = {"category": cat}
        self.category_value= category_value # here i used self to store category value because of an issue
        # it is recommended to not use self and stick to a consistent storage unit like the selection dictionary

        objInstance = ObjectId(self.id)
        doc_main = collection.find_one({"_id": objInstance})
        categories = doc_main.get("categories", [])
        #displays the chosen category options
        opts = []
        for category in categories:
            if cat in category:
                options = category.get("options", [])
                for option in options:
                    for key in option.keys():
                        if key.startswith("opt"):
                            opts.append(option[key])

        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"size_opt{idx+1}_{opt}") for idx, opt in enumerate(opts)],
            [InlineKeyboardButton("back", callback_data="back_to_main")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("please select an option", reply_markup=reply_markup)


    async def display_size(self, update: Update, context: CallbackContext):
        #retrieves user's choice of option
        query = update.callback_query
        parts = query.data.split("_")

        opt = parts[1]
        name = parts[2]
        #store it
        selection = context.user_data["selection"]
        selection["OptionNumber"] = opt
        selection["OptionName"] = name

        cat = selection.get("category")

        objInstance = ObjectId(self.id)
        doc_main = collection.find_one({"_id": objInstance})
        categories = doc_main.get("categories", [])
        # display sizes and other products' details for the chosen option by the user
        # can be modified based on the dataset and the type of products
        sizes = []
        price = None
        detail = None
        main_img = None
        message = None
        for category in categories:
            if cat in category:
                for option in category.get("options", []):
                    if opt in option:
                        detail = option.get("detail", "")
                        price = option.get("price", "")
                        main_img = option.get("img", "")
                        sizes = option.get("sizes", [])
                        message = (
                            f"name of the item chosen:  {name}\n\n"
                            f"texture :  {detail}\n\n"
                            f"price :  {price}\n\n\n"
                            "to display available colors please select your size "
                            "if you are not sure about your size press 'i do not know my size' button "
                        )

        selection["price"] = price

        size_buttons = [
            [InlineKeyboardButton(s["size"], callback_data=f"colors_{s['size']}") for s in sizes],
            [InlineKeyboardButton("back", callback_data="back_to_options")],
            [InlineKeyboardButton("i do not know my size", callback_data="table")],
        ]
        reply_markup = InlineKeyboardMarkup(size_buttons)
        #opens a folder of images assigned to the user's choice of product and send it in the conversation
        images= []
        with os.scandir(main_img) as entries:
            for entry in entries:
                if entry.is_file():
                    images.append(entry.path)

        media = [InputMediaPhoto(media=open(image, 'rb')) for image in images]
        selection ['images']= images[0]

        if media:
            await update.effective_chat.send_media_group(media=media)
        await query.edit_message_text(message, reply_markup=reply_markup)


    async def colors(self, update: Update, context: CallbackContext):
        #retrieves user's choice of size, store it, and display color
        query = update.callback_query
        parts = query.data.split("_")
        size = parts[1]

        selection = context.user_data["selection"]
        selection["size"] = size

        name = selection.get("OptionName")
        opt = selection.get("OptionNumber")
        cat = selection.get("category")
        price = selection.get("price")

        objInstance = ObjectId(self.id)
        doc_main = collection.find_one({"_id": objInstance})
        categories = doc_main.get("categories", [])

        colors = []

        for category in categories:
            if cat in category:
                options = category.get("options", [])
                for option in options:
                    if opt in option:
                        sizes = option.get("sizes", [])
                        for obj in sizes:
                            if size == obj.get("size"):
                                colors = obj.get("colors", [])
                                break
        color_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(l['color'], callback_data=f"check_{l['color']}") for l in colors],
                [InlineKeyboardButton("back", callback_data="back_to_size")]
            ]
        )
        await query.edit_message_text("select a color", reply_markup=color_buttons)

    async def check(self, update: Update, context: CallbackContext):
        #checks if the selected product of size and color is available in the stock
        query = update.callback_query
        parts = query.data.split("_")
        color = parts[1]

        if "selection" not in context.user_data:
            logging.error("Selection not found in context.user_data")
            await query.edit_message_text("something went wrong, please try later",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("back", callback_data="back_to_colors")]]))
            return

        selection = context.user_data["selection"]
        selection["color"] = color

        name = selection.get("OptionName")
        opt = selection.get("OptionNumber")
        cat = selection.get("category")
        price = selection.get("price")
        siz = selection.get("size")

        objInstance = ObjectId(self.id)
        doc_main = collection.find_one({"_id": objInstance})
        categories = doc_main.get("categories", [])

        availability = None

        for category in categories:
            if cat in category:
                for option in category.get("options", []):
                    if opt in option:
                        for size in option.get("sizes", []):
                            if siz == size.get("size"):
                                for obj in size.get("colors", []):
                                    if color == obj.get("color"):
                                        availability = obj.get("availability")
                                        break

        if int(availability) == 0:
            await query.edit_message_text("we are sorry, the option you selected is out of stock",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("رجوع", callback_data="back_to_colors")]]))

        elif int(availability) < 1:
            await query.edit_message_text("something went wrong, please try later",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("back", callback_data="back_to_colors")]]))

        else:
            keyboard = [
                [InlineKeyboardButton("view my cart", callback_data="displayCart")],
                [InlineKeyboardButton("back", callback_data="back_to_colors")],
                [InlineKeyboardButton("authorized access", callback_data="auth")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("the item you wished is available in the stock!😍",
                                          reply_markup=reply_markup)


    async def add2Cart(self, update: Update, context: CallbackContext):
        # Add current selection to the user's cart
        category_value = self.category_value

        user_cart = context.user_data.get('cart', [])

        selection = context.user_data['selection'] # gets user selection

        selection['category_value'] = category_value #adds new key

        user_cart.append(selection)

        context.user_data['cart'] = user_cart

        # Clear the selection to prevent overlapping data
        context.user_data['selection'] = None

        await self.displayCart(update, context)

    async def displayCart(self, update: Update, context: CallbackContext):
        query = update.callback_query

        # Get the user's cart from the context
        items = context.user_data.get('cart', [])
        summary_list = []
        for idx, item in enumerate(items):
            n = idx + 1
            name = item['OptionName']
            price = item['price']
            size = item['size']
            color = item['color']
            context.user_data['color'] = color

            summary_item = (
                f"item {n}\n"
                f"item's name: {name}\n"
                f"size: {size}\n"
                f"color: {color}\n"
                f"price: {price}\n"
            )
            summary_list.append(summary_item)
        summary = "\n\n".join(summary_list)
        caption = "#your cart#"
        context.user_data['summary'] = summary
        keyboard = [
                [InlineKeyboardButton("confirm order", callback_data="location")],
                [InlineKeyboardButton("add another item", callback_data="addanother")],
                [InlineKeyboardButton("delete cart", callback_data="cancel_cart")],
                [InlineKeyboardButton("back", callback_data="back2check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(caption+summary, reply_markup=reply_markup)

    async def addanother(self, update: Update, context: CallbackContext):
        await self.purchase(update, context)

    async def location(self, update: Update, context: CallbackContext):
        #requires user's location manually, because of delivery company instructions
        query = update.callback_query
        dict_loc = locations.find_one({"cities": {"$exists": True}})
        context.user_data['selection'] = None
        #minimizes user's input by displaying cities and sub regions to select from
        cities = dict_loc.get('cities')
        city_names = [city['name'] for city in cities]

        buttons = [InlineKeyboardButton(f"{item}", callback_data=f"city_{item}") for item in city_names]
        keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]  # create rows of 3 buttons each

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a city", reply_markup=reply_markup)

    async def process_location(self, update: Update, context: CallbackContext):
        #retrieves user's selection and displays sub regions
        query = update.callback_query
        dict_loc = locations.find_one({"cities": {"$exists": True}})

        cities = dict_loc.get('cities')
        city_names = [city['name'] for city in cities]

        if query.data.startswith("city_"):
            chosen_city = query.data.split("_")[1]
            context.user_data['city'] = chosen_city
            sub_regions = next((city['sub_regions'] for city in cities if city['name'] == chosen_city), None)
            if sub_regions:
                buttons = [InlineKeyboardButton(f"{item}", callback_data=f"sub_{item}") for item in sub_regions]
                keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]  # create rows of 3 buttons each
                sub_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("select a region", reply_markup=sub_markup)

    async def summarize_location(self, update: Update, context: CallbackContext):
        query = update.callback_query
        chosen_city = context.user_data['city']
        sub_region = query.data.split("_")[1]
        context.user_data['sub'] = sub_region
        text= "`" + "street" + "`" #uses a keyword for the user to copy and make sure to use in order for the bot to recognize the message
        message = (
            f"city: {chosen_city}\n"
            f"region: {sub_region}\n"
            "\n \n"
            f"please send street adress for smoother delivery{text}\n \n"
        )
        await update.effective_chat.send_message(message, parse_mode="MarkdownV2")

    async def request_phone(self, update: Update, context: CallbackContext):
        message = update.message.text
        sub_region=  context.user_data['sub']
        chosen_city = context.user_data['city']
        user_location = (
            f"city: {chosen_city}\n"
            f"region: {sub_region}\n"
            f"street adress: {message}\n"
        )
        context.user_data['user_location'] = user_location
        reply = (
            f"city: {chosen_city}\n"
            f"region: {sub_region}\n"
            f"street adress: {message}\n"
            
            "please send a valid phone number to confirm your order"
        )
        if chosen_city == "karbala" or chosen_city== "baghdad": #specific cities with lower delivery cost
            context.user_data['delivery_cost'] = 5
        else:
            context.user_data['delivery_cost'] = 6
        await update.message.reply_text(reply)

    async def phone_verified(self, update: Update, context: CallbackContext):
        phone = update.message.text
        if phone.isdigit() and len(phone) == 11 and phone.startswith('07'):
            await update.message.reply_text("order was confirmed thank you!."
                                          )
            cart = context.user_data.get('cart', []) #retrieves user cart from add2Cart
            total_price= [] #price
            delivery_cost = context.user_data['delivery_cost'] #price
            colors = [] #retrieve color and images from user cart in order to send it back to the group chat
            images = []
            for item in cart: #this loop will serve two things at the same time as it iterates over the user cart, price and images&colors
                price = item['price'].split(",")[0]
                total_price.append(int(price))
                colors.append(item['color'])
                images.append(item['images'])
            total_price.append(delivery_cost) #price
            sum_price= sum(total_price) #price
            summary = context.user_data['summary'] #user detail
            user_location = context.user_data['user_location'] #user detail
            phone_number = phone #user detail
            reply =(
                "summary: \n\n"
                f"{summary}\n\n"
                f"total price: {sum_price}\n\n"
                f" cutomer location: {user_location}\n\n"
                f"customer phone_number: {phone_number}\n\n"
                "thanks for choosing our products!"
            )


            combined = {i: (colors[i], images[i]) for i in range(len(colors))}
            # this will make it possible to send media group with its correspanding color in the cart
            # that was required by the manager and is specific to the buisness needs

            for key in combined:
                colors = combined[key][0]
                paths = combined[key][1]
                await context.bot.send_photo(chat_id=self.GROUP_CHAT_ID, photo=paths, caption= colors)
            await update.message.reply_text(reply)
            await context.bot.send_message(chat_id= self.GROUP_CHAT_ID, text=reply)


            for item in cart:
                category = item['category']
                OptionNumber = item['OptionNumber']
                OptionName = item['OptionName']
                size = item['size']
                color = item['color']
                category_value = item['category_value']
                reduce_availability('MySmallBuisness', 'Products', category, category_value, OptionNumber, OptionName,
                                    size, color)
        else:
            await update.message.reply_text(
                    "please send a valid phone number starting with 07 and is total of 11 numbers.")





    async def cancel_cart(self, update: Update, context: CallbackContext):
        query = update.callback_query
        context.user_data['cart']= None
        await query.edit_message_text("your cart has been deleted sucessfully")


    async def auth(self, update: Update, context: CallbackContext):
        user = update.effective_chat.username

        if str(user) not in self.auth_users:
            await update.effective_chat.send_message("unathoruized access",
                                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='back_to_check')]]
                ))
        else:
            await update.effective_chat.send_message(text="access granted",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("assign return", callback_data="increment")]]))


    async def increment(self, update: Update, context: CallbackContext):
        cart = context.user_data.get('cart', [])
        for item in cart:
            category = item['category']
            OptionNumber = item['OptionNumber']
            OptionName = item['OptionName']
            size = item['size']
            color = item['color']
            category_value = item['category_value']
            increment_availability('MySmallBuisness', 'Products', category, category_value, OptionNumber, OptionName,
                                size, color)
        await update.effective_chat.send_message(text="item was returned sucessfully")

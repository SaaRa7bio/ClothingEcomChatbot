This project is an English adaptation of a chatbot initially developed for an Iraqi clothing e-commerce platform.

This project contains the following files:

1. bot.py: This is the main file that runs the bot. It uses the Bot class to handle the bot's functionality. The bot has several methods to handle user interactions, such as starting the bot, displaying product categories, handling customer service requests, and more.
2. logic.py: This file contains the logic for handling various aspects of the bot, such as displaying product categories, handling user selections, and managing the user's cart. It uses the MongoDB class to interact with the MongoDB database.
3. mongodb.py: This file contains the implementation for interacting with a MongoDB database. It has methods for adding and removing items from the database, as well as methods for managing the availability of products.

Prerequisites
-------------

To run this project, you need to have the following installed:

- Python 3.x
- MongoDB
- Telegram Bot API token

Setup
-----

1. Install the required packages by running the following command:

   pip install -r requirements.txt

2. Set up the MongoDB database by creating a new database and a collection with the following structure:

   {
       "_id": ObjectId("..."),
       "categories": [
           {
               "cat1": {
                   "options": [
                       {
                           "opt1": {
                               "price": "100",
                               "img": "path/to/image",
                               "sizes": [
                                   {
                                       "size": "S",
                                       "colors": [
                                           {
                                               "color": "Red",
                                               "availability": 10
                                           },
                                           ...
                                       ]
                                   },
                                   ...
                               ]
                           }
                       },
                       ...
                   ]
               }
           },
           ...
       ]
   }

3. Set the MONGO_URI environment variable to the URI of your MongoDB instance.

4. Set the TELEGRAM_BOT_TOKEN environment variable to the API token of your Telegram bot.

5. Run the bot by executing the following command:

   python bot.py

Bot Functionality
----------------

The bot has the following functionality:

- Displaying product categories
- Displaying product options based on the selected category
- Displaying product sizes based on the selected option
- Displaying product colors based on the selected size
- Adding items to the user's cart
- Displaying the user's cart
- Confirming the user's order
- Requesting the user's location
- Requesting the user's phone number
- Verifying the user's phone number
- Sending the user's order details to the group chat
- Deleting the user's cart
- Authorized access for updating the stock
- Incrementing the availability of a product


Testing
-------

The bot can be tested by adding it to a Telegram group and interacting with it. The bot's functionality can be tested by following the steps outlined in the "Bot Functionality" section.

Deployment
----------

The bot can be deployed to a server or a cloud platform, such as Heroku or AWS. The deployment process will vary depending on the platform used.

Contributing
------------

Contributions to this project are welcome. If you would like to contribute, please submit a pull request.

License
-------

This project is licensed under the MIT License.
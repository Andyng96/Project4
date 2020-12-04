from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField
import main_functions
import requests

app = Flask(__name__)
app.config["SECRET_KEY"]="hfPMB0aUY$mb1LpCI0aAuT6P^s!PUX8T1b5gAezq%UlX@l%qh^gus8QhOjxhzus24TZ@VOrHpg!j9n4c2yEEzH%eCf4wM1sy&K@"
app.config["MONGO_URI"] = "mongodb+srv://AndyCOP4813:PYx35MHp3FP8SjbV@expenses.go22c.mongodb.net/expenses?retryWrites=true&w=majority"
mongo = PyMongo(app)
expense_db = mongo.db.expenses


class Expenses(FlaskForm):
    description = StringField("Description")
    category = SelectField("Category",
                           choices=[('rent', 'Rent'),('gas','Gas'),
                                    ('restaurant', 'Restaurant'), ('util', 'Utils'),
                                    ('groceries', 'Groceries'), ('entretaiment', 'Entretaiment'),
                                    ('hobby','Hobbies'), ('cards', 'Card Payment'), ('tolls', 'Tolls'),
                                    ('traveling','Traveling'), ('car','Car'),('insurance','Insurance'),
                                    ('others', 'Others')])
    cost = DecimalField("Cost")
    currency = SelectField("Currency",
                           choices=[('USD', 'US Dollars'), ('USDEUR', 'Euro'),
                                    ('USDCUC','Cuban Peso Convertible'),('USDCUP', 'Cuban Pesos'),
                                   ('USDMXN', 'Mexican Peso'), ('USDVEF', 'Bolivar'),
                                   ('USDCAD', 'Canadian Dollar'), ('USDJPY', 'Yen'),
                                    ('USDBZD', 'Belize Dollar'), ('USDARS', 'Argentine Peso')])

    date = DateField('Expense Date', format='%m/%d/%Y')


def get_total_expenses(category):
    get_category = expense_db.find({"category": category})
    my_category_total = 0;

    for i in get_category:
        my_category_total += float(i["cost"])

    return round(my_category_total,2)

def currency_converter(cost,currency):
    url="http://api.currencylayer.com/live?"
    my_key_dict = main_functions.read_from_file("JSON_Files/api_keys.json")
    my_key = "access_key=" + my_key_dict["my_currency_key"]

    final_url = url + my_key

    get_api = requests.get(final_url).json()
    main_functions.save_to_file(get_api, "JSON_Files/response.json")
    api_response_dic = main_functions.read_from_file("JSON_Files/response.json")

    if currency == "USD":
        converted_cost = float(cost)
    else:
        countries = api_response_dic['quotes']
        quote = countries[currency]
        converted_cost = float(cost) / float(quote)

    return round(converted_cost,2)

@app.route('/')
def index():
    my_expenses = expense_db.find({},{"cost":1})
    total_cost=0
    for i in my_expenses:
        total_cost+=float(i["cost"])

    expensesByCategory = [
        (get_total_expenses('rent'), 'Rent'), (get_total_expenses('gas'), 'Gas'),
        (get_total_expenses('restaurant'), 'Restaurant'), (get_total_expenses('util'), 'Utils'),
        (get_total_expenses('groceries'), 'Groceries'), (get_total_expenses('entretaiment'), 'Entretaiment'),
        (get_total_expenses('hobby'), 'Hobbies'), (get_total_expenses('cards'), 'Card Payment'), (get_total_expenses('tolls'), 'Tolls'),
        (get_total_expenses('traveling'), 'Traveling'), (get_total_expenses('car'), 'Car'), (get_total_expenses('insurance'), 'Insurance'),
        (get_total_expenses('others'), 'Others')]

    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    expeses_Form = Expenses(request.form)

    if request.method == "POST":
        description = request.form['description']
        category = request.form['category']
        cost = request.form['cost']
        currency = request.form['currency']
        date = request.form['date']

        cost = currency_converter(cost,currency)

        my_added_expense = [{'description': description, 'category': category, 'cost': cost, 'date': date}]
        expense_db.insert_one(my_added_expense[0])

        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expeses_Form)

app.run(debug = True, port=8080)
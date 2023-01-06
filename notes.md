```py

buying_price = db.Column(db.String(), nullable=True)

def calculate_profit(self):
    selling_price = int(self.price)
    buying_price = int(self.product.buying_price)
    return selling_price - buying_price


form.city.choices = [(city.id, city.name) for city in City.query.filter_by(state='CA').all()]
```
# forms
```py
class Form(FlaskForm):
    state = SelectField('state', choices=[('CA', 'California'), ('NV', 'Nevada')]) 
    city = SelectField('city', choices=[])
```
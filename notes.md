```py
form.city.choices = [(city.id, city.name) for city in City.query.filter_by(state='CA').all()]
```
# forms
```py
class Form(FlaskForm):
    state = SelectField('state', choices=[('CA', 'California'), ('NV', 'Nevada')]) 
    city = SelectField('city', choices=[])
```
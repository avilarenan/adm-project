Interpretador de lançamentos contábeis
====================

Basta escrever em linguagem natural o lançamento contábil que a aplicação construirá o livro diário, caixa e balanço patrimonial.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Development Setup

* `pipenv install`

* `pipenv shell`

* `python app.py`

## Deploy

* `heroku create`

* `heroku addons:create heroku-postgresql:hobby-dev`

* `git push heroku master`

* Note: make sure you run `db.create_all()` to create the tables.

## Contributors

* [Renan](https://github.com/avilarenan)
* [Fabio](https://github.com/)

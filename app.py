# coding=utf-8

import os, re

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////tmp/flask_app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)


class Lancamento(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  descricao = db.Column(db.String(100))
  valor = db.Column(db.String(300))
  de_onde = db.Column(db.String(100))
  para_onde = db.Column(db.String(100))
  ativo_passivo = db.Column(db.String(100))

  def __init__(self, descricao, valor, de_onde, para_onde, ativo_passivo):
    self.descricao = descricao
    self.valor = valor
    self.de_onde = de_onde
    self.para_onde = para_onde
    self.ativo_passivo = ativo_passivo


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html', lancamentos=Lancamento.query.all())

def lancamento_processor(raw_lancamento):
  # Interpreta o lancamento

  # Ex:
  # Comprei 20Kg de presunto por 100 Reais

  raw_lancamento = request.form['lancamento']

  value = value_identifier(raw_lancamento)
  ativo_passivo = ativo_passivo_identifier(raw_lancamento)
  de_onde = "caixa"
  para_onde = "loja"

  lanc = Lancamento(raw_lancamento, value, de_onde, para_onde, ativo_passivo)

  return lanc

def value_identifier(sentence):
  #Identifica o valor na sentenca, retorna o valor
  value_indicators = ['reais', 'real', 'RS$', '$', 'US$', 'dólar', 'dolar', 'dólares', 'dolares',]

  sentence = sentence.split()
  
  matches = [element in sentence for element in value_indicators]
  
  if len(matches) == 0:
      return False
  
  matching_indicator_indexes = [i for i, x in enumerate(matches) if x]
  
  unit_value_match = value_indicators[matching_indicator_indexes[0]]
  
  unit_value_index = sentence.index(unit_value_match)
  
  number_pattern = re.compile("^\d*$")
  
  unit_left_adjacent_word = sentence[unit_value_index-1]
  unit_right_adjacent_word = sentence[unit_value_index+1]
  
  if number_pattern.match(unit_left_adjacent_word):
      return unit_left_adjacent_word
  elif number_pattern.match(unit_right_adjacent_word):
      return unit_right_adjacent_word
  else:
      return False

def ativo_passivo_identifier(sentence):
    #retorna "ativo" se for ativo e retorna o número de parcelas se for passivo
    
    sentence = 'dummy ' + sentence + ' dummy' # for not running out of index
    
    #Identifica o valor na sentenca, retorna o valor
    passivo_indicators = ['prazo', 'parcelado', 'parcelas', 'vez', 'vezes', 'parcela',]
    
    passivo_unit_indicators = ['vezes', 'vez', 'mês', 'mes', 'meses', 'parcela', 'parcelas']

    sentence = sentence.split()
    
    matches = [element in sentence for element in passivo_indicators]
    
    if len(matches) == 0:
        return "ativo"
    
    matching_unit_indicators = [element in sentence for element in passivo_unit_indicators]
    
    matching_unit_indicator_indexes = [i for i, x in enumerate(matching_unit_indicators) if x]
    
    if len(matching_unit_indicator_indexes) == 0:
        return "ativo"
    
    unit_value_match = passivo_unit_indicators[matching_unit_indicator_indexes[0]]
    
    unit_value_index = sentence.index(unit_value_match)
    
    number_pattern = re.compile("^\d*$")
    
    unit_left_adjacent_word = sentence[unit_value_index-1]
    unit_right_adjacent_word = sentence[unit_value_index+1]
    
    if number_pattern.match(unit_left_adjacent_word):
        return unit_left_adjacent_word
    elif number_pattern.match(unit_right_adjacent_word):
        return unit_right_adjacent_word
    else:
        return False

@app.route('/lancamento', methods=['POST'])
def lancamento():
  raw_lancamento = request.form['lancamento']
  lanc_db_obj = lancamento_processor(raw_lancamento) 

  db.session.add(lanc_db_obj)
  db.session.commit()
  
  return redirect(url_for('index'))

if __name__ == '__main__':
  db.create_all()
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
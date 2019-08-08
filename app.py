# coding=utf-8

import os, re
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from re import sub
from decimal import Decimal
import time
import nltk
import nltk.corpus

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False
        
def value_identifier(sentence):
  #Identifica o valor na sentenca, retorna o valor
  value_indicators = ['reais', 'real', 'R$', '$', 'US$', 'dólar', 'dolar', 'dólares', 'dolares', 'dollars' 'dollar']

  sentence = 'dummy ' + sentence + ' dummy' # for not running out of index

  sentence = sentence.split()
  print(sentence)
  matches = [element in sentence for element in value_indicators]
  print(matches)
  if len(matches) == 0:
      return False
  
  matching_indicator_indexes = [i for i, x in enumerate(matches) if x]
  print(matching_indicator_indexes)
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
        return "passivo " + unit_left_adjacent_word
    elif number_pattern.match(unit_right_adjacent_word):
        return "passivo " + unit_right_adjacent_word
    else:
        return False

def compare_root(word1, word2):
    if len(word1) > len(word2):
        smaller = word2
        bigger = word1
    else:
        smaller = word1
        bigger = word2
    for letter in range(len(smaller)):
        if(smaller[letter].lower() != bigger[letter].lower()):
            return False
    return smaller

def in_list(element, list):
    for i in list:
        if element.lower() == i.lower():
            return True
    return False

def position(element, list):
    cont = 0
    for i in list:
        if element.lower() == i.lower():
            return cont
        cont += 1
    return -1
    
def origin_identifier(sentence):
    #retorna uma tupla com (Origem, Destino) da transação
    
    #Identifica o valor na sentenca, retorna o valor
    indicators_roots = ['compr', 'mand', 'pag', 'entreg', 'emprest', 'emprést', 'deposit', 'vend', 'invest',
                               ]
    known_clients = ['BB', 'banco', 'Banco', 'Santander', 'Itaú', 'Bradesco', 'distribuidora', 'cliente', 'clientes', 'reparo', 'reparos',
                     ]
    sentence = sentence.split()
    word_count = 0
    if(in_list('capital', sentence) and in_list('social', sentence)):
        if(position('capital', sentence) == position('social', sentence) -1):
            return 'capital social', 'caixa'
    client = 'noone'
    client_position = -1
    for word in sentence:
        word = word.replace(',', '')
        if in_list(word, known_clients):
           client = word
           client_position = position(client, known_clients)
           
    #print(sentence)
            
    for word in sentence:
        i = [int(s) for s in word if s.isdigit()]
        if(len(i)):
            print("Número!")
            print(word)
        else:
            indicator_position = 0
            for element in indicators_roots:
                indicator = compare_root(element, word)
                if(indicator):
                    indicator_position = word_count
                    break

        word_count += 1
        if (indicator == 'compr' or indicator == 'deposit'
        or indicator == 'mand' or indicator == 'pag' or indicator == 'entreg'):
            #print(client_position)
            #print(indicator_position)
            if (client_position > indicator_position) or (client == 'noone'):
                return "caixa", client
                
            else:
                return client, "caixa"
        elif (indicator == 'vend' or indicator == 'emprest'
              or indicator == 'emprést'):
            if(client == 'reparo'):
                return 'cliente', 'caixa'
            #colocar os bancos antes (client_position < maior_banco -> é um banco)
            if (client_position > indicator_position) or (client == 'noone') or client_position < 6:
                return client, "caixa"
            else:
                return "caixa", client
        elif indicator == 'invest':
            if(client == 'noone'):
                return 'capital social', 'caixa'
            else:
                return 'caixa', client

def lancamento_processor(raw_lancamento):
  # Interpreta o lancamento

  # Ex:
  # Comprei 20Kg de presunto por 100 Reais

  raw_lancamento = request.form['lancamento']

  value = value_identifier(raw_lancamento)
  ativo_passivo = ativo_passivo_identifier(raw_lancamento)
  de_onde, para_onde = origin_identifier(raw_lancamento)

  lanc = Lancamento(raw_lancamento, value, de_onde, para_onde, ativo_passivo)

  return lanc

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html', lancamentos=Lancamento.query.all())

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
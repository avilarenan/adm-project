import re
from re import sub
from decimal import Decimal

import time


import nltk
import nltk.corpus
#print(nltk.corpus.mac_morpho.tagged_words())

#money = 'R$6,150,593.22'
#value = Decimal(sub(r'[^\d.]', '', money))
#nltk.download()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

sentence = "entregou $30000 para o banco Bradesco"#input()
sentence2 = "recebeu $30000 do banco Bradesco"
wordList = re.sub("[^\w]", " ",  sentence).split()
wordList2 = re.sub("[^\w]", " ",  sentence2).split()

sentences = ["entregou $30000 para o banco Bradesco",
             "INVESTIMENTO inicial de capital no valor de $ 10.000 em dinheiro",
             "Compra a vista de móveis e utensílios, na importância de $ 2.000",
             "Compra de peças para reparos, nas seguintes condições: $ 500 a vista e $ 1000 a prazo",
             "Venda a prazo de $ 500 de peças para reparos, pelo preço de custo e a prazo",
             "Compra de peças para reparos, nas seguintes condições: $ 500 a vista e $ 1000 a prazo",
             "Venda a prazo de $ 500 de peças para reparos, pelo preço de custo e a prazo",
             "Compra de um veículo, a prazo, por $ 600, mediante o aceite de uma letra de câmbio",
             "Pagamento de 50 % da dívida relativa à compra de peças para reparo",
             "Obtenção de um empréstimo de $ 5.000, no BANCO, mediante a emissão de uma nota promissória",
             "Investimento, aumentando o capital, em mais $ 5.000, sendo $ 2.500 em dinheiro e $ 2.500 em peças",
             "Venda a vista de $ 200 em peças para reparo, pelo preço de custo",
             "Recebimento do valor de venda a prazo referente ao item 4.",
             ]
'''
print(wordList)
print(wordList2)

tag_words = []

for sentence in range(len(sentences)):
    tag_words.append(nltk.word_tokenize(sentences[sentence], language='portuguese'))

print(tag_words)
'''
#tag_word = nltk.word_tokenize(sentence, language='portuguese')
#tag_word2 = nltk.word_tokenize(sentence2, language='portuguese')

#print(nltk.pos_tag(tag_word))

#print(tag_word)
#print(tag_word2)
'''
print("################################################")
for s in range(len(sentences)):
    for i in range(len(tag_words[s])): 
        start = time.time()
        printed = False
        for word in nltk.corpus.mac_morpho.tagged_words():
            if(tag_words[s][i] == "$"):
                print(tag_words[s][i])
                printed = True
                break
            if(is_number(tag_words[s][i])):
                print("VALOR:")
                print(tag_words[s][i])
                printed = True
                break
            if(word[0].lower() == tag_words[s][i].lower()):
                print(word[0].lower())
                print(word[1])
                printed = True
                break
        if(not printed):
            print("NÃO ACHEI:")
            print(tag_words[s][i])
            break
'''
        
def value_identifier(sentence):
  #Identifica o valor na sentenca, retorna o valor
  value_indicators = ['reais', 'real', 'R$', '$', 'US$', 'dólar', 'dolar', 'dólares', 'dolares', 'dollars' 'dollar']

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
        return unit_left_adjacent_word
    elif number_pattern.match(unit_right_adjacent_word):
        return unit_right_adjacent_word
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
    #retorna uma tupla com [Origem, Destino] da transação
    
    #Identifica o valor na sentenca, retorna o valor
    indicators_roots = ['compr', 'mand', 'pag', 'entreg', 'emprest', 'emprést', 'deposit', 'vend', 'invest',
                               ]
    known_clients = ['BB', 'banco', 'Banco', 'Santander', 'Itaú', 'Bradesco', 'distribuidora', 'cliente', 'clientes', 'reparo', 'reparos',
                     ]
    sentence = sentence.split()
    word_count = 0
    if(in_list('capital', sentence) and in_list('social', sentence)):
        if(position('capital', sentence) == position('social', sentence) -1):
            return ['capital social', 'caixa']
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
                return ["caixa", client]
                
            else:
                return [client, "caixa"]
        elif (indicator == 'vend' or indicator == 'emprest'
              or indicator == 'emprést'):
            if(client == 'reparo'):
                return ['cliente', 'caixa']
            #colocar os bancos antes (client_position < maior_banco -> é um banco)
            if (client_position > indicator_position) or (client == 'noone') or client_position < 6:
                return [client, "caixa"]
            else:
                return ["caixa", client]
        elif indicator == 'invest':
            if(client == 'noone'):
                return ['capital social', 'caixa']
            else:
                return ['caixa', client]
            
print("################################")
frase = sentences[12]
print(frase)
print(origin_identifier(frase))

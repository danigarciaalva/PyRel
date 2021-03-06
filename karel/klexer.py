# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import sys
from kutil import KarelException

"""
El analizador léxico de Karel completamente reescrito por mi para la
sintaxis pascal
"""

class klexer(object):
    """analizador léxico de karel"""
    ESTADO_ESPACIO = ' '
    ESTADO_PALABRA = 'a'
    ESTADO_COMENTARIO = '#'
    ESTADO_NUMERO = '0'
    ESTADO_SIMBOLO = '+'
    def __init__(self, archivo, nombre_archivo='', debug=False):
        """Se construye el analizador con el nombre del archivo"""
        self.archivo = archivo
        self.nombre_archivo = nombre_archivo

        self.numeros = "0123456789"
        self.palabras = "abcdfeghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
        self.simbolos = "(){}*/;," #Simbolos permitidos para esta sintaxis
        self.espacios = " \n\r\t"

        self.caracteres = self.numeros+self.palabras+self.simbolos+self.espacios

        self.ultimo_caracter = ''
        self.caracter_actual = ''
        self.abrir_comentario = '' #Indica cómo fue abierto un comentario

        self.pila_tokens = [] #Pila de tokens por si me lo devuelven
        self.pila_chars = [] #Pila de caracteres
        self.char_pushed = False #Indica cuando un caracter ha sido puesto en la pila

        self.linea = 1 #El número de linea
        self.columna = 0#El número de columna
        self.tiene_cambio_de_linea = False
        self.token = ''
        self.estado = self.ESTADO_ESPACIO

        self.debug = debug
        if self.debug:
            print "leyendo archivo '%s'"%self.nombre_archivo

    def lee_caracter(self):
        """Lee un caracter de la fuente o devuelve uno de la pila si no
        está vacía"""
        if len(self.pila_chars)!=0:
            return self.pila_chars.pop()
        else:
            self.ultimo_caracter = self.caracter_actual
            return self.archivo.read(1)

    def get_token(self):
        """Obtiene el siguiente token. Si la pila tiene tokens le quita
        uno, si no, obtiene el siguiente token del archivo"""
        if len(self.pila_tokens)>0:
            return self.pila_tokens.pop()
        else:
            return self.lee_token()

    def push_token(self, token):
        """Empuja un token en la pila"""
        self.pila_tokens.append(token)

    def push_char(self, char):
        """Pone un caracter en la pila de caracteres"""
        self.pila_chars.append(char)
        self.char_pushed = True

    def lee_token(self):
        """Lee un token del archivo"""
        while True:
            self.caracter_actual = self.lee_caracter()
            self.columna += 1
            if not self.caracter_actual:
                break
            if self.tiene_cambio_de_linea:
                self.linea += 1
                self.tiene_cambio_de_linea = False
            if self.estado == self.ESTADO_COMENTARIO:
                if self.debug:
                    print "Encontré", repr(self.caracter_actual), "en estado comentario"
                if self.caracter_actual in self.simbolos: #Lo que puede pasar es que sea basura o termine el comentario
                    if self.caracter_actual == ')' and self.abrir_comentario == '(*' and self.ultimo_caracter == '*':
                        self.estado = self.ESTADO_ESPACIO
                    if self.caracter_actual == '}' and self.abrir_comentario == '{':
                        self.estado = self.ESTADO_ESPACIO
                elif self.caracter_actual == '\n':
                    self.tiene_cambio_de_linea = True
                    self.columna = 0
            elif self.estado == self.ESTADO_ESPACIO:
                if self.debug:
                    print "Encontré", repr(self.caracter_actual), "en estado espacio"
                if self.caracter_actual not in self.caracteres:
                    raise KarelException("Caracter desconocido en la linea %d columna %d"%(self.linea, self.columna))
                if self.caracter_actual in self.numeros:
                    self.token += self.caracter_actual
                    self.estado = self.ESTADO_NUMERO
                elif self.caracter_actual in self.palabras:
                    self.token += self.caracter_actual
                    self.estado = self.ESTADO_PALABRA
                elif self.caracter_actual in self.simbolos:
                    self.push_char(self.caracter_actual) #Podria ser algo valido como ();,
                    self.estado = self.ESTADO_SIMBOLO
                elif self.caracter_actual == '\n':
                    self.tiene_cambio_de_linea = True
                    self.columna = 0
            elif self.estado == self.ESTADO_NUMERO:
                if self.debug:
                    print "Encontré", repr(self.caracter_actual), "en estado número"
                if self.caracter_actual not in self.caracteres:
                    raise KarelException("Caracter desconocido en la linea %d columna %d"%(self.linea, self.columna))
                if self.caracter_actual in self.numeros:
                    self.token += self.caracter_actual
                elif self.caracter_actual in self.palabras: #Encontramos una letra en el estado numero, incorrecto
                    raise KarelException("Este token no parece valido, linea %d columna %d"%(self.linea, self.columna))
                elif self.caracter_actual in self.simbolos:
                    self.estado = self.ESTADO_SIMBOLO
                    self.push_char(self.caracter_actual)
                    break
                elif self.caracter_actual in self.espacios:
                    if self.caracter_actual == '\n':
                        self.tiene_cambio_de_linea = True
                        self.columna = 0
                    self.estado = self.ESTADO_ESPACIO
                    break #Terminamos este token
            elif self.estado == self.ESTADO_PALABRA:
                if self.debug:
                    print "Encontré", repr(self.caracter_actual), "en estado palabra"
                if self.caracter_actual not in self.caracteres:
                    raise KarelException("Caracter desconocido en la linea %d columna %d"%(self.linea, self.columna))
                if self.caracter_actual in self.palabras+self.numeros:
                    self.token += self.caracter_actual
                elif self.caracter_actual in self.simbolos:
                    self.estado = self.ESTADO_SIMBOLO
                    self.push_char(self.caracter_actual)
                    break
                elif self.caracter_actual in self.espacios:
                    if self.caracter_actual == '\n':
                        self.tiene_cambio_de_linea = True
                        self.columna = 0
                    self.estado = self.ESTADO_ESPACIO
                    break #Terminamos este token
            elif self.estado == self.ESTADO_SIMBOLO:
                if self.debug:
                    print "Encontré", repr(self.caracter_actual), "en estado símbolo"
                if self.caracter_actual not in self.caracteres:
                    raise KarelException("Caracter desconocido en la linea %d columna %d"%(self.linea, self.columna))
                if self.caracter_actual == '{':
                    self.abrir_comentario = '{'
                    self.estado = self.ESTADO_COMENTARIO
                elif self.caracter_actual in self.numeros:
                    self.estado = self.ESTADO_NUMERO
                    self.push_char(self.caracter_actual)
                    break
                elif self.caracter_actual in self.palabras:
                    self.estado = self.ESTADO_PALABRA
                    self.push_char(self.caracter_actual)
                    if self.token:
                        break
                elif self.caracter_actual in self.simbolos:
                    if self.ultimo_caracter == "(" and self.caracter_actual == '*':
                        self.token = ''
                        self.estado = self.ESTADO_COMENTARIO
                        self.abrir_comentario = '(*'
                    elif self.caracter_actual != '(': #el único símbolo con continuación
                        self.token += self.caracter_actual
                        #  self.push_char(self.caracter_actual)
                        break
                    else:
                        self.token += self.caracter_actual
                elif self.caracter_actual in self.espacios:
                    if self.caracter_actual == '\n':
                        self.tiene_cambio_de_linea = True
                        self.columna = 0
                    self.estado = self.ESTADO_ESPACIO
                    #break #Terminamos este token
        token = self.token
        self.token = ''
        return token

    def __iter__(self):
        return self

    def next(self):
        """Devuelve un token de la pila si no está vacía o devuelve el
        siguiente token del archivo, esta función sirve al iterador de
        tokens"""
        token = self.get_token()
        if token == '':
            raise StopIteration
        return token


if __name__ == '__main__':
    debug=0
    if '-d' in sys.argv:
        debug=1
    if len(sys.argv)>1:
        lexer = klexer(open(sys.argv[1]), sys.argv[1], debug=debug)
    else:
        lexer = klexer(sys.stdin, debug=debug)
    i=0
    for token in lexer:
        print "Token:", repr(token), "\t\tLine:", lexer.linea
        i += 1
    print "Hubo", i, "tokens"

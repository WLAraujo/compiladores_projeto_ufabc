##########################################################################################################
# Nesse arquivo estamos construindo o analisador léxico, ele quebra nosso código caractere a caractere   #
# numa tentaiva de associar cada palavra do código a tokens. Um token está sempre associado a um tipo e, #
# opcionalmente, a um valor. A representação dos token costuma ser simples e clara.                      #
##########################################################################################################

import erros
import string

#############################
## Definição de Constantes ##
#############################

digitos = '0123456789'
letras = string.ascii_letters
letras_e_digitos = letras + digitos

##################################
## Posição do Analisador Léxico ##
##################################

# Nessa classe pretendemos manter o rastro da posição em que o nosso analisador léxico está, assim podemos identificar onde está o erro
class Position:

    # Construtor da classe que caracteriza uma posição
    def __init__(self, index, lin, col, nome_arq, texto_arq):
        self.index = index
        self.col = col
        self.lin = lin
        self.nome_arq = nome_arq
        self.texto_arq = texto_arq

    # Método que avança para a próxima linha e coluna
    def avanc(self, char_atual = None):
        self.index += 1
        self.col += 1
        if char_atual == '\n':
            self.lin += 1
            self.col = 0
        return self
    
    # Método que retorna a posição atual
    def copia(self):
        return Position(self.index, self.lin, self.col, self.nome_arq, self.texto_arq)

#######################################
## Definição das Palavras Reservadas ##
#######################################

palavras_reservadas = [
    'VAR',
    'E',
    'OU',
    'NAO',
    'SE',
    'MAS_SE',
    'SENAO',
    'ENTAO',
    'PARA',
    'ATE',
    'C_PASSO',
    'REALIZE',
    'ENQUANTO',
    'FUN'
]

##########################
## Definição dos Tokens ##
##########################

T_INT = "INT" # Inteiro
T_FLOAT = "FLOAT" # Real
T_PLUS = "PLUS" # Mais
T_MINUS = "MINUS" # Menos
T_DIV = "DIV" # Divisão
T_MULT = "MULT" # Multiplicação
T_LPAREN = "LPAREN" # Parentêses Esquerdo
T_RPAREN = "RPAREN" # Parentêses Direito
T_EOF = "EOF" # Fim do Arquivo
T_POW = "POW" # Potência
T_KEYWORD = "KEYWORD" # Palavra Reservada Para Declarar Variável
T_IDENTIFICADOR = "IDENT" # Identificador de Variável
T_EQ = "EQ" # Atribuidor
T_EHIGUAL = "EIGUAL" # É igual
T_NIGUAL = "NIGUAL" # Não é igual
T_MENORQ = "MENORQ" # Menor que
T_MAIORQ = "MAIORQ" # Maior que
T_MENORIGUALQ = "MENORIGUALQ" # Menor igual que
T_MAIORIGUALQ = "MAIORIGUALQ" # Maior igual que
T_VIRG = 'VIRGULA' # Virgula
T_SETA = 'SETA' # Seta ->
T_STRING = 'STRING' # STRING

class Token:

    # Inicializador da classe
    def __init__(self, tipo, valor='', pos_com = None, pos_fim = None):
        self.tipo = tipo
        self.valor = valor
        if pos_com:
            self.pos_com = pos_com.copia()
            self.pos_fim = pos_com.copia()
            self.pos_fim.avanc()
        if pos_fim:
            self.pos_fim = pos_fim.copia()

    # Método para representação em conjunto com o token
    def __rep__(self):
        if self.valor:
            return f'{self.tipo}:{self.valor} '
        else:
            return f'{self.tipo} '

    # Método que verifica se o token possui o tipo e o valor também passados
    def token_bate(self, tipo_token, valor):
        return self.tipo == tipo_token and self.valor == valor

####################################
## Definição do Analisador Léxico ##
####################################

class Lexico:

    # Inicializador da classe
    def __init__(self, texto, nome_arq):
        self.texto = texto
        self.pos = Position(-1, 0, -1, nome_arq, texto) # mantém atualizada a posição atual
        self.char_atual = None # guarda o caractere atualmente atualizado
        self.nome_arq = nome_arq
        self.avan()
        

    # Avança para a próxima posição do texto
    def avan(self):
        self.pos.avanc(self.char_atual)
        self.char_atual = self.texto[self.pos.index] if self.pos.index < len(self.texto) else None

    # Método que associa os tokens
    def cria_tokens(self):
        tokens = []
        # Loop que passa por cada caractere
        while self.char_atual != None:
            if self.char_atual in " \t":
                self.avan()
            elif self.char_atual in digitos:
                tokens.append(self.cria_num())
            elif self.char_atual in letras:
                tokens.append(self.cria_ident())
            elif self.char_atual == '+':
                tokens.append(Token(T_PLUS, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '-':
                tokens.append(self.cria_menos_ou_seta())
            elif self.char_atual == '*':
                tokens.append(Token(T_MULT, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '/':
                tokens.append(Token(T_DIV, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '(':
                tokens.append(Token(T_LPAREN, pos_com=self.pos))
                self.avan()
            elif self.char_atual == ')':
                tokens.append(Token(T_RPAREN, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '"':
                tokens.append(self.cria_string())
            elif self.char_atual == '^':
                tokens.append(Token(T_POW, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '!':
                # O método abaixo verifica se o próximo char é um igual
                token, erro = self.cria_neh_igual()
                if erro:
                    return [], erro
                tokens.append(token)
                self.avan()
            elif self.char_atual == '=':
                tokens.append(self.cria_eh_igual())
                self.avan()
            elif self.char_atual == '>':
                tokens.append(self.cria_eh_maior_igual())
                self.avan()
            elif self.char_atual == '<':
                tokens.append(self.cria_eh_menor_igual())
                self.avan()
            elif self.char_atual == ',':
                tokens.append(Token(T_VIRG, pos_com=self.pos))
                self.avan()
            else:
                pos_inicio = self.pos.copia()
                char = self.char_atual
                self.avan()
                return [], erros.ErroCharIlegal(f'Erro no caractere {char}', pos_inicio = pos_inicio)
        tokens.append(Token(T_EOF, pos_com=self.pos))
        return tokens, None

    # Método que define se o número é válido e qual seu formato            
    def cria_num(self):
        str_num = ''
        pontos = 0
        pos_com = self.pos.copia()
        while self.char_atual != None and self.char_atual in digitos + '.':
            if self.char_atual == '.':
                if pontos == 1:
                    break
                pontos += 1
                str_num += '.'
            else:
                str_num += self.char_atual
            self.avan()
        if pontos == 0:
            return Token(T_INT, int(str_num), pos_com = pos_com)
        else:
            return Token(T_FLOAT, float(str_num), pos_com = pos_com)

    # Método que cria tokens para identificadores de variáveis
    def cria_ident(self):
        nome_id = ''
        pos_com = self.pos.copia()
        while self.char_atual != None and self.char_atual in letras_e_digitos + '_':
            nome_id += self.char_atual
            self.avan()
        if nome_id in palavras_reservadas:
            tipo_token = T_KEYWORD
        else:
            tipo_token = T_IDENTIFICADOR
        return Token(tipo_token, nome_id, pos_com)
    
    def cria_neh_igual(self):
        pos_com = self.pos.copia()
        self.avan()
        if self.char_atual == "=":
            self.avan()
            return Token(T_NIGUAL, pos_com=pos_com), None
        else:
            self.avan()
            return None, erros.ErroCharEsperado("'=' é esperado após '!'", self.pos_com)

    def cria_eh_igual(self):
        tikpo_token = T_EQ
        pos_com = self.pos.copia()
        self.avan()
        if self.char_atual == '=':
            self.avan()
            tikpo_token = T_EHIGUAL
        return Token(tikpo_token, pos_com=pos_com)

    def cria_eh_maior_igual(self):
        tikpo_token = T_MAIORQ
        pos_com = self.pos.copia()
        self.avan()
        if self.char_atual == '=':
            self.avan()
            tikpo_token = T_MAIORIGUALQ
        return Token(tikpo_token, pos_com=pos_com)

    def cria_eh_menor_igual(self):
        tikpo_token = T_MENORQ
        pos_com = self.pos.copia()
        self.avan()
        if self.char_atual == '=':
            self.avan()
            tikpo_token = T_MENORIGUALQ
        return Token(tikpo_token, pos_com=pos_com)

    # Método que decide se o que temos é uma seta ou sinal de menos
    def cria_menos_ou_seta(self):
        tipo_token = T_MINUS
        pos_com = self.pos.copia()
        self.avan()
        if self.char_atual == '>':
            self.avan()
            tipo_token = T_SETA
        return Token(tipo_token, pos_com = pos_com)

    def cria_string(self):
        string = ''
        pos_com = self.pos.copia()
        caracter_escape = False
        self.avan()
        caracteres_escape = {
        '-n': '\n',
        '-t': '\t'
        }
        while self.char_atual != None and (self.char_atual != '"' or caracter_escape):
            # Caracteres de escape
            if caracter_escape:
                string += caracteres_escape.get(self.char_atual)
            else:
                if self.char_atual == '\\':
                    caracter_escape = True
                else:
                    string += self.char_atual
            self.avan()
            caracter_escape = False
        self.avan()
        return Token(T_STRING, string, pos_com)


#########################
## Função de Interface ##
#########################    

# Método usado como interface para outros módulos usados ao longo do projeto, no caso do analisador léxico vamos criar os tokens com o método abaixo
def interface(texto, nome_arq):
    lexer = Lexico(texto, nome_arq)
    tokens, erro = lexer.cria_tokens()
    return tokens, erro
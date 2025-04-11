import re


LABELS = {
    "TIPO_LABEL",
    "DATA_LABEL",
    "LOCAL_LABEL",
    "RELATO_LABEL",
    "ENVOLVIDOS_LABEL",
    "OBJETOS_LABEL",
}

TOKEN_REGEX = {
    "TIPO_LABEL": r"tipo:",
    "DATA_LABEL": r"data:",
    "LOCAL_LABEL": r"local:",
    "RELATO_LABEL": r"relato:",
    "ENVOLVIDOS_LABEL": r"envolvidos:",
    "OBJETOS_LABEL": r"objetos:",
    "PALAVRA": r"[0-9]+|[a-zA-ZàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]+(-[a-zA-ZàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]+)*",
    "DATA": r"[0-3][0-9]/[0-1][0-9]/[0-9][0-9]",
    "HORA": r"[0-2][0-9]:[0-5][0-9]",
    "PONTUACAO": r"[.,;]",
    "NATUREZA": r"furto|roubo|perda|ameaça|acidente|estelionato",
}

WS_PATTERN = re.compile(r"[ \t\r\n]+")


class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.current_pos = 0
        self.current_token = None
        self.current_token_type = None

    def skip_ws(self):
        match = WS_PATTERN.match(self.input_text, self.current_pos)
        if match:
            self.current_pos = match.end()

    def lookahead(self):
        self.skip_ws()

        if self.current_pos >= len(self.input_text):
            return None

        for token_type, regex in TOKEN_REGEX.items():
            pattern = re.compile(regex)
            match = pattern.match(self.input_text, self.current_pos)
            if match:
                return token_type

        raise SyntaxError("Nenhum token encontrado")

    def match(self, expected_type):
        self.skip_ws()

        if self.current_pos >= len(self.input_text):
            self.current_token = None
            self.current_token_type = expected_type
            raise SyntaxError(
                f"Token do tipo {expected_type} esperado após fim do arquivo"
            )

        regex = TOKEN_REGEX[expected_type]
        pattern = re.compile(regex)

        match = pattern.match(self.input_text, self.current_pos)

        if match:
            self.current_token = match.group(0)
            self.current_token_type = expected_type
            self.current_pos = match.end()
            return self.current_token

        raise SyntaxError(f"Nenhum token do tipo {expected_type} encontrado")


class Parser:
    def __init__(self, input_text):
        self.lexer = Lexer(input_text)

    def start(self):
        self.ocorrencias()

    def ocorrencias(self):
        self.registro()
        try:
            while True:
                self.registro()
        except SyntaxError as e:
            if e.msg == "Token do tipo TIPO_LABEL esperado após fim do arquivo":
                return
            else:
                raise e

    def registro(self):
        self.lexer.match("TIPO_LABEL")
        self.natureza()
        self.lexer.match("DATA_LABEL")
        self.data_hora()
        self.lexer.match("LOCAL_LABEL")
        self.local()
        self.lexer.match("RELATO_LABEL")
        self.descricao()
        self.lexer.match("ENVOLVIDOS_LABEL")
        self.envolvidos()
        self.lexer.match("OBJETOS_LABEL")
        self.objetos()

    def natureza(self):
        self.lexer.match("NATUREZA")

    def data_hora(self):
        self.lexer.match("DATA")
        try:
            self.lexer.match("HORA")
        except SyntaxError:
            pass

    def local(self):
        self.palavras()

    def descricao(self):
        self.palavras()

    def envolvidos(self):
        self.palavras()

    def objetos(self):
        self.palavras()

    def palavras(self):
        self.lexer.match("PALAVRA")
        while True:
            try:
                token = self.lexer.match("PONTUACAO")
                if token != ".":
                    break
            except SyntaxError:
                pass

            tk_type = self.lexer.lookahead()
            if tk_type in LABELS:
                return
            break
        while True:
            try:
                token = self.lexer.match("PALAVRA")
            except SyntaxError as e:
                if self.lexer.current_token is None and token not in [",", ";"]:
                    break
                else:
                    raise e
            try:
                token = self.lexer.match("PONTUACAO")
                if token != ".":
                    continue
            except SyntaxError:
                pass

            tk_type = self.lexer.lookahead()
            if tk_type in LABELS:
                break


if __name__ == "__main__":
    with open("input.txt", "r", encoding="utf-8") as file:
        input_text = file.read()

    parser = Parser(input_text)
    try:
        parser.start()
        print("Entrada válida!")
    except SyntaxError as e:
        print("Erro de sintaxe:", e)

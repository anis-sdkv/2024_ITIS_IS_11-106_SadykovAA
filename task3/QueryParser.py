from task2.TextProcessor import TextProcessor


class QueryParser:
    def __init__(self):
        self.operations = "!&|()"
        self.precedence = {
            '!': 3,
            '&': 2,
            '|': 1
        }
        self.text_processor = TextProcessor()

    def convert_to_rpn(self, query):
        """Преобразует строку запроса в обратную польскую нотацию"""
        input_tokens = self._get_query_tokens(query)
        input_tokens = [token if token in self.operations else self.text_processor.lemmatize_morph(token)
                        for token in input_tokens]
        return self._convert_tokens_to_rpn(input_tokens)

    def _convert_tokens_to_rpn(self, input_tokens):
        """Преобразует массив токенов в обратную польскую нотацию"""
        output_expression = []
        operator_stack = []

        for token in input_tokens:
            if token not in self.operations:
                output_expression.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != "(":
                    output_expression.append(operator_stack.pop())
                if operator_stack:  # Проверка на случай несбалансированных скобок
                    operator_stack.pop()  # Удаляем открывающую скобку
            else:
                while (operator_stack and operator_stack[-1] != "(" and
                       token in self.precedence and
                       operator_stack[-1] in self.precedence and
                       self.precedence[token] <= self.precedence[operator_stack[-1]]):
                    output_expression.append(operator_stack.pop())
                operator_stack.append(token)

        # Помещаем оставшиеся операторы в выходную строку
        while operator_stack:
            output_expression.append(operator_stack.pop())

        return output_expression

    @staticmethod
    def _get_query_tokens(query):
        """Разбивает запрос на токены, заменяя русские операторы на символы"""
        operator_map = {'и': '&', 'или': '|', 'не': '!'}
        query = query.lower().split(' ')
        query = ''.join([operator_map.get(token, token) for token in query])

        tokens = []
        current_word = []

        for char in query:
            if char in "()&|!":
                if current_word:
                    tokens.append("".join(current_word))
                    current_word = []
                tokens.append(char)
            else:
                current_word.append(char)

        if current_word:
            tokens.append("".join(current_word))

        return tokens

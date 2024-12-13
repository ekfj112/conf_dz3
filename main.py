import sys
import re
import xml.etree.ElementTree as ET
from math import fabs


# Функция для обработки и вычисления выражений
def evaluate_expression(expression):
    try:
        # Обрабатываем выражения, заключенные в символы | |
        def evaluate_in_pipes(match):
            inner_expr = match.group(1)  # Внутри | |
            return str(evaluate_expression(inner_expr))

        # Находим все выражения между | |
        expression = re.sub(r'\|([^|]+)\|', evaluate_in_pipes, expression)

        # Заменяем вызовы функции pow(x, y) на x ** y
        expression = re.sub(r'pow\(([^,]+),\s*([^)]+)\)', r'(\1 ** \2)', expression)

        # Заменяем вызовы abs(x) на fabs(x)
        expression = expression.replace('abs', 'fabs')

        # Используем eval, чтобы вычислить выражение
        return eval(expression)
    except Exception as e:
        raise ValueError(f"Ошибка при вычислении выражения: {expression} -> {str(e)}")


# Функция для преобразования XML в конфигурационный язык
def transform_to_config(xml_string):
    root = ET.fromstring(xml_string)
    config_output = ""

    # Преобразуем XML в нужный формат
    for elem in root:
        if elem.tag == 'comment':
            # Многострочный комментарий
            config_output += f"/*\n{elem.text}\n*/\n"
        elif elem.tag == 'array':
            # Массив
            config_output += f"({' '.join(elem.text.split())})\n"
        elif elem.tag == 'dict':
            # Словарь
            config_output += "{\n"
            for item in elem:
                key = item.get('key')
                value = item.text.strip()
                config_output += f"  {key} -> {value}.\n"
            config_output += "}\n"
        elif elem.tag == 'let':
            # Объявление константы
            name = elem.get('name')
            value = elem.text.strip()
            try:
                evaluated_value = evaluate_expression(value)
                config_output += f"let {name} = {evaluated_value};\n"
            except ValueError as e:
                print(e, file=sys.stderr)
                return ""
        elif elem.tag == 'expression':
            # Вычисление выражения
            expr = elem.text.strip()
            try:
                evaluated_value = evaluate_expression(expr)
                config_output += f"|{evaluated_value}|\n"
            except ValueError as e:
                print(e, file=sys.stderr)
                return ""
        else:
            print(f"Неизвестный элемент: {elem.tag}", file=sys.stderr)
            return ""

    return config_output


# Основная функция обработки командной строки
def main():
    if len(sys.argv) != 3:
        print("Использование: python script.py <input_xml_file> <output_config_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, 'r') as f:
            xml_string = f.read()

        # Преобразуем XML в конфигурацию
        config_output = transform_to_config(xml_string)
        if config_output:
            with open(output_file, 'w') as f:
                f.write(config_output)
            print(f"Конфигурация успешно записана в {output_file}")
        else:
            print("Ошибка при преобразовании XML.")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

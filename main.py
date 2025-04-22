import random, re


class BasicInterpreter:
    def __init__(self):
        self.variables = {}
        self.program = {}
        self.current_line = None

    def parse_line(self, line):
        if line.upper() in ['RUN', 'LIST', 'CLEAR', 'EXIT']:
            return line.upper(), None
        if ' ' not in line:
            return None, None
        try:
            num, command = line.strip().split(' ', 1)
            return int(num), command.strip()
        except ValueError:
            return None, None

    def load_line(self, line):
        line_number, command = self.parse_line(line)
        if isinstance(line_number, int):
            self.program[line_number] = command
            self.program = dict(sorted(self.program.items()))
        return line_number

    def list_program(self):
        for num in sorted(self.program):
            print(f"{num} {self.program[num]}")

    def clear_program(self):
        self.program = {}
        self.variables = {}

    def eval_expression(self, expr):
        expr = expr.strip()

        # Replace BASIC-style comparisons
        expr = expr.replace("<>", "!=")
        if '=' in expr and '==' not in expr and all(op not in expr for op in ['<', '>', '!', '==']):
            expr = expr.replace('=', '==')

        # Replace variables using word boundaries
        for var in sorted(self.variables, key=lambda x: -len(x)):  # longest first
            val = self.variables[var]
            if isinstance(val, str):
                val_str = f'"{val}"'
            else:
                val_str = str(val)
            expr = re.sub(rf'\b{re.escape(var)}\b', val_str, expr)

        return eval(expr)

    def run(self):
        lines = sorted(self.program.keys())
        index = 0
        for_stack = []

        while index < len(lines):
            self.current_line = lines[index]
            command = self.program[self.current_line]
            parts = command.strip().split(' ', 1)
            keyword = parts[0].upper()

            arg = parts[1] if len(parts) > 1 else ""

            if keyword == 'PRINT':
                print(self.eval_expression(arg))

            elif keyword == 'LET':
                var, expr = arg.split('=', 1)
                self.variables[var.strip()] = self.eval_expression(expr.strip())

            elif keyword == 'INPUT':
                var = arg.strip()
                self.variables[var] = input("> ")
            elif keyword == 'RANDOM':
                self.variables["R"] = random.randint(0,10)
            elif keyword == 'GOTO':
                target = int(arg.strip())
                if target in self.program:
                    index = lines.index(target)
                    continue
                else:
                    print(f"Line {target} not found")
                    break



            elif keyword == 'IF':
                condition, then_part = arg.upper().split('THEN')
                if self.eval_expression(condition.strip()):
                    target = int(then_part.strip())
                    if target in self.program:
                        index = lines.index(target)
                        continue
                    else:
                        print(f"Line {target} not found")
                        break



            elif keyword == 'FOR':
                var, rest = arg.split('=', 1)
                start, end = rest.strip().split('TO')
                var = var.strip()
                start_val = self.eval_expression(start.strip())
                end_val = self.eval_expression(end.strip())
                self.variables[var] = start_val
                for_stack.append((var, end_val, self.current_line))

            elif keyword == 'NEXT':
                if not for_stack:
                    print("NEXT without FOR")
                    break
                var, end_val, for_line = for_stack[-1]
                self.variables[var] += 1
                if self.variables[var] <= end_val:
                    index = lines.index(for_line)
                    continue
                else:
                    for_stack.pop()
            elif keyword == 'INPUTINT':
                var = arg.strip()
                try:
                    self.variables[var] = int(input(f"{var}? "))
                except ValueError:
                    print(f"Invalid integer. {var} set to 0.")
                    self.variables[var] = 0

            else:
                print(f"Unknown command: {command}")
            index += 1


# --- BASIC REPL (type in your program)
def basic_repl():
    interpreter = BasicInterpreter()
    print("Mini BASIC Interpreter. Type your program. Type RUN to execute, LIST to view, CLEAR to reset, EXIT to quit.")
    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue
            if line.upper() == "RUN":
                interpreter.run()
            elif line.upper() == "LIST":
                interpreter.list_program()
            elif line.upper() == "CLEAR":
                interpreter.clear_program()
                print("Program cleared.")
            elif line.upper() == "EXIT":
                print("Goodbye!")
                break
            elif line.upper().startswith("SAVE"):
                _, *filename = line.strip().split(maxsplit=1)
                filename = filename[0] if filename else "program.bas"
                try:
                    with open(filename, "w") as f:
                        for num in sorted(interpreter.program):
                            f.write(f"{num} {interpreter.program[num]}\n")
                    print(f"Program saved to '{filename}'")
                except Exception as e:
                    print(f"Error saving file: {e}")

            elif line.upper().startswith("LOAD"):
                _, *filename = line.strip().split(maxsplit=1)
                filename = filename[0] if filename else "program.bas"
                try:
                    with open(filename, "r") as f:
                        interpreter.clear_program()
                        for line in f:
                            interpreter.load_line(line.strip())
                    print(f"Program loaded from '{filename}'")
                except FileNotFoundError:
                    print(f"File '{filename}' not found.")
                except Exception as e:
                    print(f"Error loading file: {e}")

            else:
                num = interpreter.load_line(line)
                if num is None:
                    print("Invalid input. Use line numbers or commands like RUN, LIST.")
        except Exception as e:
            print(f"Error: {e}")

# Run the BASIC REPL
basic_repl()

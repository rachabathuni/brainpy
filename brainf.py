from collections import deque
import sys


class EndOfProgramException(Exception):
    pass


class TapeOutOfBoundsException(Exception):
    pass


class InvalidLoopException(Exception):
    pass


class InvalidProgramCounterException(Exception):
    pass


class UnknownInstructionException(Exception):
    pass


def handle_inc(exec_state):
    exec_state.inc_cur_cell()
    exec_state.prog_next()


def handle_dec(exec_state):
    exec_state.dec_cur_cell()
    exec_state.prog_next()


def handle_print(exec_state):
    sys.stdout.write(chr(exec_state.get_cur_cell()))
    sys.stdout.flush()
    #print(exec_state.get_cur_cell())
    exec_state.prog_next()


def handle_tape_prev(exec_state):
    exec_state.tape_prev()
    exec_state.prog_next()


def handle_tape_next(exec_state):
    exec_state.tape_next()
    exec_state.prog_next()


def handle_loop_begin(exec_state):
    lf = exec_state.get_loop_frame()
    exec_state.push_loop_frame(lf)
    exec_state.prog_next()


def handle_loop_end(exec_state):
    lf = exec_state.pop_loop_frame()
    if not lf:
        raise InvalidLoopException

    if exec_state.get_cell_value(lf.loop_counter_cell):
        exec_state.push_loop_frame(lf)
        exec_state.set_program_counter(lf.loop_begin_pc)
    exec_state.prog_next()


INSTRUCTIONS = {
        "+": handle_inc,
        "-": handle_dec,
        ".": handle_print,
        "<": handle_tape_prev,
        ">": handle_tape_next,
        "[": handle_loop_begin,
        "]": handle_loop_end
}


class LoopFrame:
    def __init__(self, loop_begin_pc, loop_counter_cell):
        self.loop_begin_pc = loop_begin_pc
        self.loop_counter_cell = loop_counter_cell


class ExecState:

    def __init__(self, program):
        self._program = program
        self._program_counter = 0
        self._loop_stack = deque()
        self._tape = [0]
        self._tape_pointer = 0


    def get_current_instruction(self) -> str:
        if self._program_counter < 0 or self._program_counter > len(self._program):
            raise InvalidProgramCounterException

        if self._program_counter == len(self._program):
            raise EndOfProgramException

        return self._program[self._program_counter]


    def inc_cur_cell(self):
        self._tape[self._tape_pointer] += 1


    def dec_cur_cell(self):
        self._tape[self._tape_pointer] -= 1


    def get_cur_cell(self):
        return self._tape[self._tape_pointer]


    def get_cell_value(self, cell_index):
        return self._tape[cell_index]


    def tape_next(self):
        self._tape_pointer += 1
        if self._tape_pointer == len(self._tape):
            self._tape.append(0)


    def tape_prev(self):
        self._tape_pointer -= 1
        if self._tape_pointer < 0:
            raise TapeOutOfBoundsException
    

    def prog_next(self):
        self._program_counter += 1
        if self._program_counter == len(self._program):
            if len(self._loop_stack):
                raise InvalidLoopException


    def get_loop_frame(self):
        return LoopFrame(self._program_counter, self._tape_pointer)


    def push_loop_frame(self, lf):
        self._loop_stack.append(lf)


    def pop_loop_frame(self):
        try:
            return self._loop_stack.pop()
        except IndexError as ie:
            return None


    def set_program_counter(self, pc):
        self._program_counter = pc


    def dump_debug(self):
        print("============= DEBUG =============")
        print(f"Program Counter: {self._program_counter}")
        if self._program_counter >=0 and self._program_counter < len(self._program):
            print("%s{%s}%s" % (self._program[:self._program_counter], self._program[self._program_counter], self._program[self._program_counter+1:]))
        print("Tape:")
        print(self._tape)
        print("==================================")


def instruction_loop(exec_state):
    while True:
        #exec_state.dump_debug()
        cur_instruction = exec_state.get_current_instruction()
        try:
            INSTRUCTIONS[cur_instruction](exec_state)
        except KeyError as ke:
            raise UnknownInstructionException


def exec(program):
    exec_state = ExecState(program)
    
    try:
        instruction_loop(exec_state)
    except EndOfProgramException as eote:
        print()
    except Exception as e:
        print("Exception: %s" % e.__class__.__name__)

    exec_state.dump_debug()


def remove_white_spaces(s) -> str:
        out = s
        out = out.replace("\n", "")
        out = out.replace("\r", "")
        out = out.replace(" ", "")
        return out


def start():
    if len(sys.argv) < 2:
        print("Usage: brainf.py <filename>")
        sys.exit(1)

    with open(sys.argv[1]) as fd:
        program = remove_white_spaces(fd.read())

    exec(program)


if __name__ == "__main__":
    start()

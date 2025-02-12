"""
File reading and writing implementations.
"""


from typing import TextIO
from numpy import ndarray
from source.qt_emulator import QTEmulator


def load(filepath: str) -> list[tuple[int, int, int]]:
    """
    Reads binary executable file, compiled by Q-Compiler
    :param filepath: executable filepath
    :return: list of instruction tuples
    """

    instructions = list()
    with open(filepath, "rb") as file:
        namespace = b''  # namespace header
        while (char := file.read(1)) != b'\x00':
            namespace += char

        # read and decode instructions
        while True:
            if namespace == b'QT':
                raw_instruction = file.read(4)
            elif namespace == b'QM':
                raw_instruction = file.read(3)
            else:
                raise Exception
            if not raw_instruction:
                break

            memory_flag = raw_instruction[0] & 1
            value = int.from_bytes(raw_instruction[1:3])
            opcode = raw_instruction[3]

            instructions.append((memory_flag, value, opcode))
    return instructions


class QTEmulatorIO:
    """
    File IO for QTEmulator
    """

    offset = 16
    index_offset = 4
    added_offset = 3
    number_offset = 5
    section_size = offset * (number_offset + 1) + index_offset + added_offset

    @classmethod
    def _create_memory_dump(cls, file: TextIO, memory: ndarray, section_name: str):
        """
        Writes dump for a given memory section
        """

        file.write(f"{'[' + section_name.upper() + ' SECTION START]':=^{cls.section_size}}\n")
        file.write(" " * (cls.index_offset + cls.added_offset))
        for i in range(cls.offset):
            file.write(f"{i: {cls.number_offset}d} ")
        for index in range(0, len(memory), cls.offset):
            file.write(
                "\n" +
                f"{index:0{cls.index_offset}d} | " +
                " ".join(f"{val:0{cls.number_offset}d}" for val in memory[index:index + cls.offset]))
        file.write(f"\n{'[' + section_name.upper() + ' SECTION END]':=^{cls.section_size}}\n\n")

    @classmethod
    def create_memory_dump(cls, filepath: str, emulator: QTEmulator):
        """
        Creates a memory dump
        """

        with open(f"{filepath}.CACHE.dmp", "w", encoding="ASCII") as file:
            cls._create_memory_dump(file, emulator.cache, "CACHE")
        with open(f"{filepath}.STACK.dmp", "w", encoding="ASCII") as file:
            cls._create_memory_dump(file, emulator.stack, "STACK")
        with open(f"{filepath}.ADDR_STACK.dmp", "w", encoding="ASCII") as file:
            cls._create_memory_dump(file, emulator.address_stack, "ADDR_STACK")
        with open(f"{filepath}.PORTS.dmp", "w", encoding="ASCII") as file:
            cls._create_memory_dump(file, emulator.ports, "PORTS")
        with open(f"{filepath}.REGISTERS.dmp", "w", encoding="ASCII") as file:
            file.write(f"{'[REGISTER SECTION START]':=^{cls.section_size}}\n")
            file.write(f"{'ACC': <4} = {emulator.accumulator.item()}\n")
            file.write(f"{'PR': <4} = {emulator.pointer_register.item()}\n")
            file.write(f"{'PC': <4} = {emulator.program_counter.item()}\n")
            file.write(f"{'FR': <4} = {emulator.flag_register.item()}\n")
            file.write(f"{'SP': <4} = {emulator.stack_pointer.item()}\n")
            file.write(f"{'ASP': <4} = {emulator.address_stack_pointer.item()}\n")
            file.write(f"{'[REGISTER SECTION END]':=^{cls.section_size}}\n")

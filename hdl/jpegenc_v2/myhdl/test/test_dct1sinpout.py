#!/bin/python
from myhdl import *
from dct1sinpout import *
from random import randrange

RANGE1_8 = range(8)

ACTIVE_LOW, INACTIVE_HIGH = False, True
INACTIVE_LOW, ACTIVE_HIGH = False, True


def print_list(signalList):
    for i in RANGE1_8:
        print "{:7d}".format(int(signalList[i])),
    print ""


def print_matrix(matrix):
    for i in RANGE1_8:
        print_list(matrix[i])


def test():
    output = PixelLine()
    input = Signal(intbv(0)[8:])
    enable_in, enable_out, clk = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = Signal(INACTIVE_HIGH)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        input.next = 0
        enable_in.next = ACTIVE_HIGH
        yield clk.negedge

        input.next = 0
        yield clk.negedge

        input.next = 0
        yield clk.negedge

        reset.next = ACTIVE_LOW
        yield clk.negedge

        reset.next = ACTIVE_LOW
        yield clk.negedge

        reset.next = INACTIVE_HIGH
        for i in RANGE1_8:
            input.next = 0
            yield clk.negedge

    @instance
    def monitor():
        while True:
            yield delay(11)
            print "\t".join(['en_out', 'input', 'en_in', 'reset',
                             ' clk', '  now'])
            print "\t".join(["  %d"]*6) % (enable_out, input, enable_in, reset,
                                           clk, now())
            print "-" * 72
            print "-" * 72
            print_list(output.pixels)
            print "-" * 72
            yield delay(9)

    dct_inst = dct1SinPout(output, enable_out, input, enable_in, clk, reset)

    sim = Simulation(clkgen, dct_inst, stimulus, monitor)
    sim.run(20 * 8 + 20*5 + 1)

if __name__ == '__main__':
    test()

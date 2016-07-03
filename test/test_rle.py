"""The functionality of entire Run Length Encoder is checked here"""

# @todo: this is temporary until `rle` parameters are updated
from argparse import Namespace as Constants

from myhdl import StopSimulation
from myhdl import block
from myhdl import ResetSignal, Signal, instance
from myhdl.conversion import verify

from jpegenc.subblocks.rle import rlencoder, InDataStream, BufferDataBus
from jpegenc.subblocks.rle import RLEConfig, Pixel

from jpegenc.testing import clock_driver, reset_on_start, pulse_reset, toggle_signal
from jpegenc.testing import run_testbench

# from testcases import *
from rle_test_inputs import (red_pixels_1, green_pixels_1, blue_pixels_1,
                             red_pixels_2, green_pixels_2, blue_pixels_2,)


def write_block(clock, block, datastream, rleconfig, color):
    """Write the data into RLE Double Buffer"""

    # select one among Y1,Y2 or Cb or Cr to be processes
    rleconfig.color_component.next = color

    # wait till start signal asserts
    yield toggle_signal(datastream.start, clock)

    # read data into rle module
    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge

    while rleconfig.read_addr != 63:
        # more reads
        datastream.input_val.next = block[rleconfig.read_addr]
        yield clock.posedge

    datastream.input_val.next = block[rleconfig.read_addr]

    # wait till all the inputs are written into RLE Double Fifo
    for _ in range(4):
        yield clock.posedge


def read_block(select, bufferdatabus, clock):
    """Outputs the data from RLE Double Buffer"""

    # select which buffer should be in read mode
    bufferdatabus.buffer_sel.next = select
    yield clock.posedge

    # enable read mode
    bufferdatabus.read_enable.next = True
    yield clock.posedge

    # pop data out into the bus until fifo becomes empty
    while bufferdatabus.fifo_empty != 1:
        print("runlength %d size %d amplitude %d" % (
            bufferdatabus.runlength,
            bufferdatabus.size, bufferdatabus.amplitude))
        yield clock.posedge

    print("runlength %d size %d amplitude %d" % (
        bufferdatabus.runlength, bufferdatabus.size, bufferdatabus.amplitude))

    # disable readmode
    bufferdatabus.read_enable.next = False
    yield clock.posedge


def test_rle():
    """This test checks the functionality of the Run Length Encoder"""
    @block
    def bench_rle():

        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        # constants for input, runlength, size width
        width = 6
        constants = Constants(width_addr=width, width_data=12,
                              max_write_cnt=63, rlength=4,
                              size=width.bit_length())
        pixel = Pixel()

        # interfaces to the rle module
        # input to the rle core and start signals sent from here
        indatastream = InDataStream(constants.width_data)

        # signals generated by the rle core
        bufferdatabus = BufferDataBus(
            constants.width_data, constants.size, constants.rlength)

        # selects the color component, manages address values
        rleconfig = RLEConfig(constants.max_write_cnt.bit_length())

        # rle double buffer constants
        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = Constants(width=width_dbuf, depth=constants.max_write_cnt + 1)

        # instantiation for clock and rletop module
        inst = rlencoder(
            dfifo_const, constants, reset, clock,
            indatastream, bufferdatabus, rleconfig
        )

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():

            # reset the stimulus before sending data in
            yield pulse_reset(reset, clock)

            # write Y1 component into 1st buffer
            bufferdatabus.buffer_sel.next = False
            yield clock.posedge
            yield write_block(
                clock, red_pixels_1,
                indatastream,
                rleconfig, pixel.Y1
                )
            yield clock.posedge
            print("============================")

            # read Y1 component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Y2 component into 2nd Buffer
            yield write_block(
                clock, red_pixels_2,
                indatastream,
                rleconfig, pixel.Y2
                )
            yield clock.posedge

            print("============================")

            # read Y2 component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write Cb Component into 1st Buffer
            yield write_block(
                clock, green_pixels_1,
                indatastream,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print("=============================")

            # read Cb component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Cb Component into 2nd Buffer
            yield write_block(
                clock, green_pixels_2,
                indatastream,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print("==============================")

            # read Cb component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write Cr Component into 1st Buffer
            yield write_block(
                clock, blue_pixels_1,
                indatastream,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print("==============================")

            # read Cr component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Cr Component into 2nd Buffer
            yield write_block(
                clock, blue_pixels_2,
                indatastream,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print("==============================")

            # read Cr component from 1st Buffer
            yield read_block(False, bufferdatabus, clock)

            print("==============================")

            # end of stream when sof asserts
            yield clock.posedge
            rleconfig.sof.next = True
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst_clock, inst

    run_testbench(bench_rle)


def test_rle_conversion():
    """This block is used to test conversion"""

    @block
    def bench_rle_conversion():

        width = 6
        constants = Constants(width_addr=width, width_data=12,
                              max_write_cnt=63, rlength=4,
                              size=width.bit_length())

        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        indatastream = InDataStream(constants.width_data)
        bufferdatabus = BufferDataBus(
            constants.width_data, constants.size, constants.rlength)

        rleconfig = RLEConfig(constants.max_write_cnt.bit_length())

        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = Constants(width=width_dbuf, depth=constants.max_write_cnt + 1)

        inst = rlencoder(
            dfifo_const, constants, reset, clock,
            indatastream, bufferdatabus, rleconfig)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            yield clock.posedge
            print("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_rle_conversion().verify_convert() == 0


if __name__ == "__main__":
    test_rle()

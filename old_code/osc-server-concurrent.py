from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import argparse

def filter_handler(address, *args):
    print(f"{address}: {args}")
    #print(args[1])

def print_calculo(unused_addr, args, parameter):
#  print("[{0}] ~ {1}".format(args[0], parameter))
  print("El doble del fader es:", 2*parameter)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="192.168.2.17", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

dispatcher = Dispatcher()
dispatcher.map("/1/fader1", filter_handler)
dispatcher.map("/1/fader1", print_calculo, "Fader")


async def loop():
    """Example main loop that only runs for 10 iterations before finishing"""
    for i in range(10):
        print(f"Loop {i}")
        await asyncio.sleep(1)


async def init_main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())
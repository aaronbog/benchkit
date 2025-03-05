#!/usr/bin/env python3
import asyncio
import subprocess
from threading import Thread
from threading import Thread
from typing import Coroutine
import asyncssh
import threading
import time

from aaronShell.src.commandlineInterface.dataStructs import CommandPassthrough

async def tester(stdout,newout):
    try:
        print("startup tester1")
        while True:
            a = await stdout.read(10)
            print(f"tester1: {a}")
            if not a:
                break
            print("before writeout")
            newout.writeOut(a)
            print("after writeout")
        newout.succeed(0)
        print("end tester1")
    except Exception as inst:
        print(inst)


async def tester2(stdout):
    print("startup tester2")
    while True:
        a = await stdout.readOut(10)
        print(f"tester2: {a}")
        if not a:
            break
    print("end tester2")


def create_event_loop_thread() -> asyncio.AbstractEventLoop:
    """
    From https://gist.github.com/dmfigol/3e7d5b84a16d076df02baa9f53271058
    """
    def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    eventloop = asyncio.new_event_loop()
    thread = Thread(target=start_background_loop, args=(eventloop,), daemon=False)
    thread.start()
    return eventloop

def run_coroutine_in_thread(coro: Coroutine,loop) -> asyncio.Future:
    """
    From https://gist.github.com/dmfigol/3e7d5b84a16d076df02baa9f53271058
    """
    return asyncio.run_coroutine_threadsafe(coro, loop)

async def create_process(connection):

    return await connection.create_process(r'echo "1\n2\n3";sleep 3;echo "4\n5\n6"',
                                                stdin=None,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)

async def create_conection():
    return await asyncssh.connect('mynameisace.site',57429,username='yoyoyoyo',encoding =None)

async def test():

    a = CommandPassthrough()
 
    loop = create_event_loop_thread()
    loop2 = create_event_loop_thread()
    futcon = run_coroutine_in_thread(create_conection(),loop)

    fut = run_coroutine_in_thread(create_process(futcon.result()),loop)
    procedure = fut.result()
    # print(await procedure.stdout.read(2))
    print(';;;;;')
    print(procedure)
    print(';;;;;')
    newout = CommandPassthrough(a.commandLinkerObject)
    fut1 = run_coroutine_in_thread(tester(procedure.stdout,newout),loop2)
    fut2 = run_coroutine_in_thread(tester2(newout),loop2)
    fut1.result()
    fut2.result()
    loop.stop()
    loop2.stop()
    print("done")

loopmain = create_event_loop_thread()
fut = run_coroutine_in_thread(test(),loopmain)
fut.result()
loopmain.stop()


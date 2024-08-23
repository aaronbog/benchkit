#!/usr/bin/env python3
import asyncio,subprocess
from threading import Thread

from aaronShell.src.commandlineInterface.dataStructs import CommandOutput, LocalCommandOutput,CommandPassthrough
from aaronShell.src.hooks.hooks import Hook, ReaderHook, WriterHook
async def hooktest(loop):

    async def basichookfunction(comandOutput:CommandOutput,nextStream:CommandPassthrough) -> None:
        # this is a verry bad way of doing it 
        while True:
            a = await comandOutput.readOut(10)
            if not a:
                break
            a = a.decode('utf-8')
            a = a.upper()
            nextStream.writeOut(bytes(a, encoding='utf-8'))
        nextStream.endWritingErr()
        nextStream.endWritingOut()

    async def readerhookfunction(comandOutput:CommandOutput) -> None:
        # this is a verry bad way of doing it 
        while True:
            a = await comandOutput.readOut(10)
            if not a:
                break
            a = a.decode('utf-8')
            print("[readerhookstart]")
            print(a,end="")
            print("[readerhookend]")

    test = WriterHook(basichookfunction)
    test2 = ReaderHook(readerhookfunction,voidStdErr=True)

    proc1 = subprocess.Popen(r'echo "a\nb\nc";sleep 2;echo "d\ne\nf"', shell=True,
                                    stdout=subprocess.PIPE)
    
    outputObj = LocalCommandOutput(proc1.stdout,proc1.stderr)
    test.startHookFunction(outputObj)
    test2.startHookFunction(test.getPassthrough())
    proc1 = subprocess.Popen(r'cat', shell=True, stdin=test2.getPassthrough().getReaderFdOut(),
                                    stdout=subprocess.PIPE)
    outputObj = LocalCommandOutput(proc1.stdout,proc1.stderr)
    print(a := await outputObj.readOut(300))
    print(a := await outputObj.readOut(300))





if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hooktest(loop))

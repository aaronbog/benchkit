#!/usr/bin/env python3
import asyncio, asyncssh, subprocess
import time
from aaronShell.src.commandAST.command import command
from aaronShell.src.commandlineInterface.commandlineInterface import LocaleInterface, RemoteInterface
from aaronShell.src.commandlineInterface.dataStructs import CommandOutput, LocalCommandOutput, SSHCommandOutput, CommandPassthrough
from aaronShell.src.hooks.hooks import ReaderHook

async def run_client() -> None:

    conn = await asyncssh.connect('ftp.mynameisace.online',57429,username='yoyoyoyo',encoding =None)

    local_proc_1 = subprocess.Popen(r'echo "1\n2\n3";cat a', shell=True,
                                    stdout=subprocess.PIPE)

    local_proc_1_out = LocalCommandOutput(local_proc_1.stdout,local_proc_1.stderr)

    remote_proc_in = CommandPassthrough()
    

    a = await local_proc_1_out.readOut(400)
    print("result locale command")
    print(a)
    remote_proc_in.writeOut(a)
    remote_proc_in.endWritingOut()
    remote_proc = await conn.create_process('cat', stdin=remote_proc_in.getReaderFdOut(),stdout=subprocess.PIPE)
    print("---------------")

    remote_proc_out = SSHCommandOutput(remote_proc.stdout,remote_proc.stderr)

    local_proc_2_in = CommandPassthrough()
    a = await remote_proc_out.readOut(400)
    print("recieved from remote")
    print(a)
    local_proc_2_in.writeOut(a)
    local_proc_2_in.endWritingOut()
    local_proc_2 = subprocess.Popen('cat', shell=True,
                                    stdin=local_proc_2_in.getReaderFdOut(),
                                    stdout=subprocess.PIPE)
    
    local_proc_2_out = LocalCommandOutput(local_proc_2.stdout,local_proc_2.stderr)

    print("---------------")
    print("back trough locale command")
    result = await local_proc_2_out.readOut(400)
    print(local_proc_2.wait())
    print(result)
    await conn.__aexit__(None,None,None)


if False:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_client())


async def interfaceTesting():
    async with (RemoteInterface('ftp.mynameisace.online',57429,username='yoyoyoyo') as remote,
                LocaleInterface() as local):
        
        
        async def readerhookfunction(comandOutput:CommandOutput) -> None:
            newout = CommandPassthrough()
            await local.run_command(command(r'cat'),input=newout)
            # this is a verry bad way of doing it 
            while True:
                a = await comandOutput.readOut(10)
                if not a:
                    break
                newout.writeOut(a)

        demoComand = command(r'ls;sleep 2;echo "4\n5\n6"').addPostRunHook(ReaderHook(readerhookfunction,voidStdErr=True))

        out = await local.run_command(demoComand)
        out2 = await remote.run_command(command("grep 'configure'"),input=out)
        r = await out2.readOut(200)
        print("output of grep")
        print(r)

if True:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(interfaceTesting())

async def CommandOutputTesting():
    local_proc_1 = subprocess.Popen(r'echo "1\n2\n3";sleep 2;ec ho "4\n5\n6"', shell=True,
                                    stdout=subprocess.PIPE)
    outputObj = LocalCommandOutput(local_proc_1.stdout,local_proc_1.stderr)
    print(type(local_proc_1.stdout))

    print(a := await outputObj.readOut(300))
    print(not not a)
    local_proc_1.stdout.close()
    print(a := await outputObj.readOut(300))
    print(not not a)

    time.sleep(3)
    print(not not await outputObj.readOut(300))
    print(not not await outputObj.readOut(300))
    

    print("remote--------------------------------------------")
    conn = await asyncssh.connect('ftp.mynameisace.online',57429,username='yoyoyoyo',encoding =None)
    remote_proc = await conn.create_process(r'echo "1\n2\n3";sleep 2;echo "4\n5\n6"',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outputObj = SSHCommandOutput(remote_proc.stdout,remote_proc.stderr)
    print(type(remote_proc.stdout))

    print(a := await outputObj.readOut(300))
    
    print(not not a)
    print(a := await outputObj.readOut(300))
    print(not not a)

    time.sleep(3)
    print(not not await outputObj.readOut(300))
    print(not not await outputObj.readOut(300))


if False:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(CommandOutputTesting())
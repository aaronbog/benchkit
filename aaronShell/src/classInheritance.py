#!/usr/bin/env python3
from aaronShell.src.commandAST.Oldcommand import SingleCommand
from aaronShell.src.commandlineInterface.commandlineInterface import CommandlineInterface
import asyncio, asyncssh, sys
from abc import ABC, abstractmethod
import subprocess

# cython https://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html#wrapping-cplusplus


# interactive remote is not working
# channel = client.get_transport().open_session()
# channel.invoke_shell()
# interactive.interactive_shell(channel)

#https://github.com/paramiko/paramiko/blob/main/demos/interactive.py
# import interactive


#https://github.com/petamas/oslex -> parsing for posix and windows

from typing import Optional

class MySSHClientSession(asyncssh.SSHClientSession):
    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        print(data, end='')

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print('SSH session error: ' + str(exc), file=sys.stderr)

class MySSHClient(asyncssh.SSHClient):
    def connection_made(self, conn: asyncssh.SSHClientConnection) -> None:
        print('Connection made to %s.' % conn.get_extra_info('peername')[0])

    def auth_completed(self) -> None:
        print('Authentication successful.')

async def run_client() -> None:
    opt = asyncssh.SSHClientConnectionOptions(username='***')
    conn, client = await asyncssh.create_connection(MySSHClient, '***',***,options=opt)


    chan, session = await conn.create_session(MySSHClientSession, 'ls')
    await chan.wait_closed()
    await conn.__aexit__(None,None,None)

if False:

    try:
        asyncio.get_event_loop().run_until_complete(run_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))

class TestBase(ABC):
    def __init__(self) -> None:
        self._a: int|None = None
    
    @abstractmethod
    def get_a(self) -> int:
        pass

    @property
    def a(self):
        return self.get_a()
    
class Test(TestBase):
    def get_a(self):
        if self._a == None:
            print("iff")
            self._a = 2
            return self._a
        print("noiff")
        return self._a

if False:
    t = Test()
    print(t.a)
    print(t.a)

if __name__ == '__main__':
    subprocess.call("dir", shell=True)

if False:


    # echo $$; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/'
    command0 = SingleCommand(Universal.ls,["-R"])
    command2 = SingleCommand("grep", ["\":$\""])
    command4 = SingleCommand("sed", ["-e", "'s/:$//'", "-e", "'s/[^-][^\\/]*\\//--/g'", "-e", "'s/^/   /'", "-e", "'s/-/|/'"])
    command  = command0.pipe(command2).pipe(command4).prependGetPid()

    samuPy = CommandlineInterface.remoteInterface(hostname="***",port=***,username="***")
    #locale = CommandlineInterface.localInterface()
    with (
        samuPy as s,
        #locale as l
        ):
        s.run_command(command)
        #l.run_command(command)

    # stdin, stdout, stderr = client.exec_command(command0.pipe(command2).pipe(command4).get_command())
    """
    stdin, stdout, stderr = client.exec_command("echo $$; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\\/]*\\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; mkdir aoeu")
    pid = int(stdout.readline())  # prepend echo $$; for the kill
    print(pid)
    # stdout.close()
    client.exec_command("kill %d" % pid)
    exit_status = stdout.channel.recv_exit_status()
    # print(exit_status)
    # out=stdout.read()
    # print(out)
    client.close()
    """
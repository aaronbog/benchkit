#!/usr/bin/env python3
import shlex
from command import Command, SingleCommand
from commandlineInterface import CommandlineInterface

# cython https://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html#wrapping-cplusplus


# interactive remote is not working
# channel = client.get_transport().open_session()
# channel.invoke_shell()
# interactive.interactive_shell(channel)

#https://github.com/paramiko/paramiko/blob/main/demos/interactive.py
# import interactive


#https://github.com/petamas/oslex -> parsing for posix and windows


if __name__ == '__main__':


    # ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/'
    command0 = SingleCommand("ls", ["-R"])
    command2 = SingleCommand("grep", ["\":$\""])
    command4 = SingleCommand("sed", ["-e", "'s/:$//'", "-e", "'s/[^-][^\/]*\//--/g'", "-e", "'s/^/   /'", "-e", "'s/-/|/'"])
    command  = command0.pipe(command2).pipe(command4)

    samuPy = CommandlineInterface.remoteInterface(hostname="_____",port=_____,username="_____")
    #locale = CommandlineInterface.localInterface()
    with (
        samuPy as s,
        #locale as l
        ):
        s.run_command(command)
        #l.run_command(command)

    # stdin, stdout, stderr = client.exec_command(command0.pipe(command2).pipe(command4).get_command())
    """
    stdin, stdout, stderr = client.exec_command("echo $$; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' ; mkdir aoeu")
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
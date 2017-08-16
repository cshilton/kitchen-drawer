#! /bin/python

import os, os.path, re, shlex, sys

from Tkinter import *

class TkSsh(Tk):

    '''A tk ssh menu program while I try to figure out how to do readline
       contexts in one of the korn shells.'''

    def BuildButtonFrame(self):

        columns = 4

        f = Frame(self)
        for i, h in enumerate(self.HostList):
            c = (i % columns)
            r = (i / columns)
            Button(f, text=h.Host, command=h).grid(row=r, column=c, sticky=NSEW, padx=4, pady=4)

        return f

    def __init__(self, **kw):

        host_list = kw.pop("host_list")

        Tk.__init__(self, **kw)

        self.wm_title("ssh: chooser")

        self.HostList = host_list

        f = self.BuildButtonFrame()
        f.pack(side=TOP)

## == Utility functions ====================================================================

class SshHost(object):

    '''A host that I can ssh to according to my ~/.ssh/config file.'''

    def __init__(self, host, host_fqdn):
        self.HostFqdn = host_fqdn
        self.Host = host

    def __str__(self):
        return self.Host

    def __repr__(self):
        cls = self.__class__
        return '%s("%s", "%s")' % (cls.__name__, self.Host, self.HostFqdn)

    def __call__(self, *args, **kw):

        try:
            my_pid = os.fork()
            if my_pid > 0:
                return

        except OSError as err:
            sys.stderr.write("fork failed: (%d) -- %s\n" % (e.errno, e.strerror))

        os.setsid()

        try:
            my_pid = os.fork()
            if my_pid > 0:
                sys.exit(0)

        except OSError as err:
            sys.stderr.write("fork failed: (%d) -- %s\n" % (e.errno, e.strerror))

        cmd = shlex.split("/bin/gnome-terminal -e \"ssh '%s'\"" % self.Host)
        os.execve(cmd[0], cmd, os.environ)
        ## Not reached.
        os._exit(os.EX_OK)

def build_host_list(ssh_config=None):

    if ssh_config is None:
        ssh_config = os.path.expanduser("~/.ssh/config")

    ssh_config = tuple([ l for l in [ rl.rstrip() for rl in open(ssh_config, "r") ] if l ])

    token_search = re.compile(r'^Host\s+[^*]')

    host_list = tuple([ tuple(l.split()[1:]) for l in ssh_config if token_search.match(l) ])

    hl = [ ]
    for ht in host_list:
        fq = ht[0]
        if len(ht) == 1:
            hl.append(SshHost(fq, fq))
        else:
            hl += [ SshHost(h, fq) for h in ht[1:] ]
    
    return tuple(hl)
    
## == tests ================================================================================

def tests():

    return 0

if __name__ == '__main__':

    hl = build_host_list()

    my_app = TkSsh(host_list=hl)
    my_app.mainloop()

    sys.exit(0)

## Local variables:
## mode: python
## python-indent-offset: 4
## fill-column: 92
## End:

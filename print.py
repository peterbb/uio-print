#!/usr/bin/env python2.7

# Copyright (c) 2013 Peter Brottveit Bock <post@peterbb.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys, os, subprocess, tempfile, shutil
import paramiko

HOST = "login.ifi.uio.no"
USERNAME="peterbb"
LOGIN = USERNAME + "@" + HOST

def main():
    args = sys.argv[1:]
    if not args:
        print "usage: %s [options] filename ..." % sys.argv[0]
        sys.exit(1)

    (args, files) = parse_args(args)

    client = create_ssh_client()

    _, stdout, _ = client.exec_command("mktemp -d printXXXXXXXX")
    tempfolder = stdout.readlines()[0][:-1]

    send_files(files, tempfolder)

    subprocess.call(["ssh", LOGIN, "print"] + args + [ tempfolder + "/*"])

    client.exec_command("rm -rf " + tempfolder)

def parse_args(args):
    files = []

    for arg in reversed(args):
        if os.path.exists(arg):
            files.append(arg)
        else:
            break

    args = args[:-len(files)]
    return (args, files)

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USERNAME)
    return client

def send_files(files, tempfolder):
    localfolder = tempfile.mkdtemp()
    newnames = []

    for n, f in enumerate(files):
        tmp_f = "%s/%d.%s" % (localfolder, n, os.path.basename(f))
        os.symlink(os.path.abspath(f), tmp_f)
        newnames += [ tmp_f ]

    subprocess.call(["scp"] + newnames + [ LOGIN + ":" + tempfolder])
    shutil.rmtree(localfolder)


if __name__ == "__main__":
    main()

import fcntl
import sys
import os


def singleton( pidfile ):
    global fp
    fp = open(pidfile, 'a+')
    pid = str(os.getpid())
    try:
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        raise SystemExit("Process already running with pid " + fp.read())
    fp.seek(0)
    fp.truncate()
    fp.write(str(os.getpid()))
    fp.flush()
    fp.seek(0)


def daemonize():
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)
    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+')
    se = open('/dev/null', 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


if __name__=="__main__":
    singleton("daemon.pid")
    #daemonize()
    import time
    import syslog
    for i in range(10):
        print "tick", i
        syslog.syslog( "tick " + repr(i) )
        time.sleep(1)

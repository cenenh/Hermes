import sys
import logging
import logging.config
import optparse
import os
import pwd
import grp
from hermes.server import run


def setup_logging(config, stdout=False):
    if stdout:
        log = logging.getLogger('hermes')
        log.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setLevel(logging.DEBUG)
        streamHandler.setFormatter(DebugFormatter())
        log.addHandler(streamHandler)
        return log
    else:
        logging.config.fileConfig(config['logging']['conf_file'])
        return logging

if __name__ == "__main__":

    try:
        # Initialize Options
        parser = optparse.OptionParser()
        parser.add_option("-c", "--configfile",
                          dest="configfile",
                          default="conf/hermes.conf",
                          help="config file")

        parser.add_option("-f", "--foreground",
                          dest="foreground",
                          default=False,
                          action="store_true",
                          help="run in foreground")

        parser.add_option("-l", "--log-stdout",
                          dest="log_stdout",
                          default=False,
                          action="store_true",
                          help="log to stdout")

        # Parse Command Line Args
        (options, args) = parser.parse_args()

        # Initial variables
        uid = -1
        gid = -1

        # Initialize Config
        options.configfile = os.path.abspath(options.configfile)
        if os.path.exists(options.configfile):
            from hermes.settings import CONF
            config = CONF.set_config(options.configfile)
        else:
            print("ERROR: Config file: %s does not exist."
                  % (options.configfile), file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(1)

        # Initialize Logging
        log = setup_logging(config, options.log_stdout)

    # Pass the exit up stream rather then handle it as an general exception
    except SystemExit as e:
        raise SystemExit

    except Exception as e:
        import traceback
        sys.stderr.write("Unhandled exception: %s" % str(e))
        sys.stderr.write("traceback: %s" % traceback.format_exc())
        sys.exit(1)

    # Switch to using the logging system
    try:
        # PID MANAGEMENT
        options.pidfile = str(config['server']['pid_file'])

        # Read existing pid file
        try:
            pf = open(options.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except (IOError, ValueError):
            pid = None

        # Check existing pid file
        if pid:
            # Check if pid is real
            if not os.path.exists("/".join(["/proc", str(pid), "cmdline"])):
                # Pid is not real
                os.unlink(options.pidfile)
                pid = None
                print("WARN: Bogus pid file was found. I deleted it.",
                      file=sys.stderr)
            else:
                print("ERROR: Pidfile exists. Server already running?",
                      file=sys.stderr)
                sys.exit(1)

        if os.name != 'nt':
            # Get final GIDs
            if len(config['server']['group']):
                gid = grp.getgrnam(config['server']['group']).gr_gid

            # Get final UID
            if len(config['server']['user']):
                uid = pwd.getpwnam(config['server']['user']).pw_uid

        # Fix up pid permissions
        if not options.foreground:
            pid = str(os.getpid())
            try:
                pf = open(options.pidfile, 'w+')
            except IOError as e:
                print("Failed to write PID file: %s" % (e), file=sys.stderr)
                sys.exit(1)
            pf.write("%s\n" % pid)
            pf.close()
            os.chown(options.pidfile, uid, gid)
            log.debug("Wrote First PID file: %s" % (options.pidfile))

        # USER MANAGEMENT
        # Switch user to specified user/group if required
        try:
            if gid != -1 and os.getgid() != gid:
                # Set GID
                os.setgid(gid)

            if uid != -1 and os.getuid() != uid:
                # Set UID
                os.setuid(uid)

        except Exception as e:
            print("ERROR: Failed to set UID/GID. %s" % (e), file=sys.stderr)
            sys.exit(1)

        # Log
        log.info('Changed UID: %d (%s) GID: %d (%s).' % (
            os.getuid(),
            config['server']['user'],
            os.getgid(),
            config['server']['group']))

        # DAEMONIZE MANAGEMENT
        # Detatch Process
        if not options.foreground:

            # Double fork to serverize process
            log.info('Detaching Process.')

            # Fork 1
            try:
                pid = os.fork()
                if pid > 0:
                    # Exit first paren
                    sys.exit(0)
            except OSError as e:
                print("Failed to fork process." % (e), file=sys.stderr)
                sys.exit(1)
            # Decouple from parent environmen
            os.setsid()
            os.umask(0)
            # Fork 2
            try:
                pid = os.fork()
                if pid > 0:
                    # Exit second paren
                    sys.exit(0)
            except OSError as e:
                print("Failed to fork process." % (e), file=sys.stderr)
                sys.exit(1)
            # Close file descriptors so that we can detach
            sys.stdout.close()
            sys.stderr.close()
            sys.stdin.close()
            os.close(0)
            os.close(1)
            os.close(2)
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')

        # PID MANAGEMENT
        # Finish Initialize PID file
        if not options.foreground:
            # Write pid file
            pid = str(os.getpid())
            try:
                pf = open(options.pidfile, 'w+')
            except IOError as e:
                log.error("Failed to write child PID file: %s" % (e))
                sys.exit(1)
            pf.write("%s\n" % pid)
            pf.close()
            # Log
            log.debug("Wrote child PID file: %s" % (options.pidfile))

        # Server Start!
        run()

    # Pass the exit up stream rather then handle it as an general exception
    except SystemExit as e:
        raise SystemExit

    except Exception as e:
        import traceback
        log.error("Unhandled exception: %s" % str(e))
        log.error("traceback: %s" % traceback.format_exc())
        sys.exit(1)

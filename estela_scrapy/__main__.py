import os
import sys
import logging


def run_scrapy(argv, settings):
    from scrapy.cmdline import execute

    # an intermediate function might be needed for other commands [!] missing
    sys.argv = argv
    execute(settings=settings)


def run_code(args, log_handler=None, commands_module=None):
    try:
        from estela_scrapy.settings import populate_settings

        # API data might be sent [!] missing
        settings = populate_settings()
        if commands_module:
            settings.set("COMMANDS_MODULE", commands_module, priority="cmdline")
        if log_handler is not None:
            log_handler.setLevel(settings["LOG_LEVEL"])
    except Exception:
        logging.exception("Settings initialization failed")
        raise
    try:
        run_scrapy(args, settings)
    except Exception:
        logging.exception("Job runtime exception")
        raise


def describe_project():
    """Describe scrapy project."""
    from estela_scrapy.env import setup_scrapy_conf

    setup_scrapy_conf()

    run_code(
        ["scrapy", "describe_project"] + sys.argv[1:],
        commands_module="estela_scrapy.commands",
    )


def setup_and_launch():
    try:
        from estela_scrapy.env import decode_job, get_args_and_env, setup_scrapy_conf

        job = decode_job()
        assert job, "JOB_INFO must be set"
        args, env = get_args_and_env(job)

        os.environ.update(env)
        setup_scrapy_conf()

        from estela_scrapy.log import init_logging

        loghdlr = init_logging()
    except:
        logging.exception("Environment variables were not defined properly")
        raise

    run_code(args, loghdlr)


def main():
    """Start the crawling process."""
    try:
        setup_and_launch()
    except SystemExit as ex:
        return ex.code
    except:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
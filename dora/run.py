from functools import partial
import os
from shutil import rmtree
import sys
import typing as tp

from .executor import start_ddp_workers
from .main import DecoratedMain
from .log import simple_log, red
from .shep import Shepherd

log = partial(simple_log, "Launch:")


def check_job_and_clear(argv: tp.List[str], main: DecoratedMain, clear: bool = False):
    """This will check if an existing job is running and warn,
    unless --clear is passed, in which case we must cancel it.
    """
    shepherd = Shepherd(main, log)
    sheep = shepherd.get_sheep_from_argv(argv)
    if sheep.job is not None:
        shepherd.update()
        if sheep.is_done():
            return
        else:
            job = sheep.job
            log(red(f"Found existing slurm job {job.job_id} with status {job.state}."))
            if clear:
                log("Cancelling the existing job.")
                shepherd.cancel_lazy(sheep.job)
                shepherd.commit()
            else:
                log(red("PLEASE ABORT NOW UNLESS YOU ARE SURE OF WHAT YOU DO."))
    if clear and sheep.xp.folder.exists():
        log("Removing existing XP folder.")
        rmtree(sheep.xp.folder)


def run_action(args, main: DecoratedMain):
    if args.ddp and not os.environ.get('RANK'):
        check_job_and_clear(args.argv, main, args.clear)
        start_ddp_workers(args.package, main, args.argv)
    else:
        if 'WORLD_SIZE' not in os.environ:
            check_job_and_clear(args.argv, main, args.clear)
            os.environ['LOCAL_RANK'] = '0'
            os.environ['RANK'] = '0'
            os.environ['WORLD_SIZE'] = '1'
        sys.argv[1:] = args.argv
        main()

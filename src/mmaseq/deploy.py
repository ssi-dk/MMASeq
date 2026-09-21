#!/usr/bin/env python3

from .__version__ import __version__
from .utils.PATH import *
from .utils.logging_setup import initiate_log, adjust_log

import argparse
import subprocess
import sys
import collections
import ftplib
import shutil
import urllib.request
from urllib.parse import urlparse

def parse_deploy():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "MMAseq deploy\n"
            "Install environments and creates databases by "
            "executing MMAseq on an inbuilt test dataset.\n"
            "Pipeline results files are written to the deployment directory."
        ),
        epilog=(
            "This is the MMAseq Deploy module.\n"
            "For details on samplesheet creation execute 'mmacreate -h'\n"
            "For details on the main module execute 'mmaseq -h'"
        )
    )

    parser.add_argument(
        "--deploy_dir",
        dest="deploy_dir",
        default=PKG_DIR / "Deploy",
        help=(
            "Directory used to deploy virtual environment and databases "
            "used during pipeline execution. To reinstall environments "
            "and/or databases, remove the `conda/` and/or the `Databases/` "
            "folders in the deployment directory. (Default: %(default)s)"
        )        
    )

    parser.add_argument(
        "--update",
        dest="update",
        action="store_true",
        help=(
            "Will force running all rules to ensure issuing database updates. "
            "(Default: %(default)s) The small dataset consists of a single "
            "isolate, executed on ALL modules, thus all results should be "
            f"considered wrong. Read data will be downloaded to {READ_DIR}"
        )
    )

    parser.add_argument(
        "--custom",
        dest="custom",
        action="store_true",
        help=(
            "Enable custom species configuration. (Default: %(default)s) "
            "When enabled, species configuration folders (identified as species_configs/ inside the deploy_dir/) will be used. "
            "If the folder doesn't allready exists, it will be copied from the install folder to the deployment directory."
        )
    )

    parser.add_argument(
        "--test",
        dest="test",
        action="store_true",
        help=(
            "Will run rules to complete a quick pipeline test. "
            "(Default: %(default)s) The test dataset consist of exactly "
            "400001 paired end reads created synthetically from AI. "
            "Certain modules will fail on these reads and are "
            " excluded from the test. "
            "Excluded; resfinder, pointfinder, kleborate, shovill"
        )
    )

    parser.add_argument(
        "--retries",
        dest="retries",
        default=3,
        type=int,
        help=(
            "Amount of attempts allowed for each file, when downloading the "
            "dataset. (Default: %(default)s) Setting this to 0 will lead to "
            "failure if any short instance of disconnect occurs. Contrarily, "
            "setting this to a too high value could lead to long run time if "
            "any continuous connection issue occurs. It's recommended to allow "
            "for a handful of attempts."
        )
    )

    parser.add_argument(
        "--threads",
        dest="threads",
        default=4,
        help=(
            "Amount of threads (cores) to dedicate for executing the pipeline. "
            "(Default: %(default)s)"
        )
    )

    parser.add_argument(
        "--verbosity",
        dest="verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help = (
            "Adjust the verbosity (Default: %(default)s); "
            "0: Minimal messages, "
            "1: Debug messages, "
            "2: Trace messages (development only)"
        )
    )

    parser.add_argument(
        "--logfile",
        dest="logfile",
        type=str,
        default=None,
        help=(
            "If provided, will redirect log messages from STDOUT to logfile. "
            "(Default: %(default)s) Will be ignored if logfile parent folder "
            "doesn't exist."
        )
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"MMAseq {__version__}",
    )

    return parser.parse_args()


def deploy_spe_configs(deploy_dir):
    logger.trace(("deploy_spe_configs(\n "
        f"deploy_dir = {deploy_dir}"
        ")"))

    species_configs = deploy_dir / "species_configs"
    
    logger.trace("Checking whether config dir allready exists")
    if not species_configs.exists():
        logger.trace(f"Couldn't locate {species_configs}, clonig from {SPE_CONFIGS}")
        shutil.copytree(SPE_CONFIGS, species_configs)
        #SPE_CONFIGS.copy(species_configs) # Use from python 3.14+ and remove import shutils
        logger.info("Copied species configs directory from installation folder into deployment dir.")
    else:
        logger.info("Species configuration directory allready exists. Skipping!")

    return None


def extract_hosts(urls):
    logger.trace(f"extract_hosts(urls = {urls})")

    hosts = collections.defaultdict(list)

    for url in urls:
        parsed_url = urlparse(url)

        host = parsed_url.netloc
        path = parsed_url.path

        hosts[host].append(path)

    return hosts

def connect_ftp(host, timeout = 15):
    logger.trace(f"Connecting to {host}")

    ftp = ftplib.FTP(host, timeout = timeout)

    # Anonymous login
    ftp.login()

    return ftp


def disconnect_ftp(ftp):
    logger.trace("Attempting to close the FTP connection.")
    try:
        ftp.quit()
        logger.trace("FTP connection soft close successful!")
    except UnboundLocalError:
        logger.trace(
            "Closing FTP failed because it was never established in the "
            "first place. This was expected behavior!"
        )
    except AttributeError:
        logger.warning(
            "FTP connection can't be terminated softly. "
            "Attempting aggressive termination!"
        )
        try:
            ftp.close()
            logger.trace("FTP connection aggressive close successful!")
        except Exception:
            logger.error("FTP disconnect failed.")


def download_ftp_file(ftp, paths, destination, max_retries):
    logger.trace(
        f"download_ftp_file(\n - ftp: {ftp}\n - paths: {paths}\n - "
        f"destination: {destination}\n - max_retries: {max_retries})"
    )

    failed_paths = []

    for path in paths:
        target_file = destination / path.split('/')[-1]
        target_chnk = target_file.with_suffix(
            f"{target_file.suffix}.chunk"
        )

        # Remove old chunks if already exists
        if target_chnk.exists():
            logger.warning(
                f"Old chunk file detected: {target_chnk} "
                "this is not intended. Removing!"
            )
            target_chnk.unlink()

        # Abort if the file exists
        if target_file.exists():
            logger.debug(
                f"File already downloaded. Skipping {target_file.name}"
            )
            continue

        logger.info(
            f"Test sample missing. Downloading {target_file.name}"
        )

        success = False
        retries = 0

        while retries <= max_retries:
            retries += 1

            try:
                logger.trace(
                    f"Downloading {target_file.name} as {target_chnk}"
                )

                with open(target_chnk, 'wb') as local_file:
                    ftp.retrbinary(
                        f'RETR {path}',
                        local_file.write
                    )

                logger.trace(
                    f"Renaming {target_chnk.name} to {target_file.name}"
                )

                target_chnk.replace(target_file)

                success = True
                break

            except Exception as e:
                logger.error(
                    f"Failed to download {path} on attempt "
                    f"#{retries}\n{e}"
                )

                if target_chnk.exists():
                    target_chnk.unlink()

        if success:
            logger.trace(
                f"{target_file.name} was successfully downloaded "
                f"into {destination}"
            )
        else:
            logger.warning(
                f"{target_file.name} failed to download via FTP!"
            )
            failed_paths.append(path)

    return failed_paths


def download_https_file(host, path, destination, max_retries):
    logger.trace(
        f"download_https_file(\n - host: {host}\n - path: {path}\n"
        f" - destination: {destination}\n - max_retries: {max_retries})"
    )

    target_file = destination / path.split('/')[-1]
    target_chnk = target_file.with_suffix(
        f"{target_file.suffix}.chunk"
    )

    if target_file.exists():
        logger.debug(
            f"File already downloaded. Skipping {target_file.name}"
        )
        return True

    url = f"https://{host}{path}"

    logger.info(
        f"Attempting HTTPS fallback for {target_file.name}: {url}"
    )

    for retries in range(1, max_retries + 2):
        try:
            logger.trace(
                f"Downloading {target_file.name} via HTTPS "
                f"(attempt #{retries})"
            )

            with urllib.request.urlopen(url, timeout=30) as response:
                with open(target_chnk, "wb") as local_file:
                    shutil.copyfileobj(response, local_file)

            logger.trace(
                f"Renaming {target_chnk.name} to {target_file.name}"
            )

            target_chnk.replace(target_file)

            logger.info(
                f"{target_file.name} successfully downloaded "
                f"via HTTPS into {destination}"
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to download {url} via HTTPS "
                f"on attempt #{retries}\n{e}"
            )

            if target_chnk.exists():
                target_chnk.unlink()

    logger.warning(
        f"{target_file.name} failed to download via HTTPS!"
    )

    return False



def deploy_dataset(update, max_retries):
    logger.trace(
        f"deploy_dataset(\n - update: {update}\n - "
        f"max_retries: {max_retries})"
    )

    with open(URL_FILE, "r") as url_file:
        urls = url_file.read().splitlines()

    # Reduce dataset size if small is selected
    size = "the full"

    if update:
        urls = urls[0:2]
        size = "a subselection of the"

    hosts = extract_hosts(urls)

    for host in hosts.keys():
        paths = hosts.get(host)

        logger.debug(
            f"Examining {host} for test dataset"
        )

        failed_paths = paths

        try:
            ftp = connect_ftp(host)

        except Exception as e:
            logger.warning(
                f"FTP connection to {host} failed. "
                f"Falling back to HTTPS.\n{e}"
            )

        else:
            try:
                failed_paths = download_ftp_file(
                    ftp,
                    paths,
                    READ_DIR,
                    max_retries
                )

            finally:
                disconnect_ftp(ftp)

        if failed_paths:
            logger.warning(
                f"{len(failed_paths)} file(s) from {host} "
                "will be attempted via HTTPS."
            )

            for path in failed_paths:
                success = download_https_file(
                    host,
                    path,
                    READ_DIR,
                    max_retries
                )

                if not success:
                    logger.error(
                        f"Failed to download {path} via both "
                        f"FTP and HTTPS."
                    )
                    raise RuntimeError(f"Unable to download dataset files")

    return None


def deploy(args):

    deploy_dir = Path(args.deploy_dir)
    update = args.update
    custom = args.custom
    test = args.test
    retries = args.retries
    threads = args.threads
    verbosity = args.verbosity

    if custom:
        logger.info("Inspecting species configuration directory")
        deploy_spe_configs(deploy_dir)

    if not test:
        logger.info(f"Inspecting the deployment dataset")
        deploy_dataset(update, retries)

    samplesheet_file = f"{DATA_DIR}/samplesheet.tsv"

    # Create arguments for command
    additional_cmds = "--resolve "
    if update:
        dataset = "small"
        samplesheet_file = f"{DATA_DIR}/samplesheet_small.tsv"
        additional_cmds += "--ignore_assemblies --force --clean "
    elif test:
        dataset = "test"
        samplesheet_file = f"{DATA_DIR}/samplesheet_test.tsv"
        additional_cmds += "--clean "
    else:
        dataset = "full"



    outdir = deploy_dir / "MMAseq_Test"
    additional_cmds += f"--clean --verbosity {verbosity} "

    if custom:
        additional_cmds += "--custom "

    # Create command
    command = (
        f"mmaseq --samplesheet {samplesheet_file} "
        f"--deploy_dir {deploy_dir} "
        f"--outdir {outdir} "
        f"--threads {threads} "
        "--resolve "
        f"{additional_cmds}"
    )
    logger.debug(f"Created command for MMAseq:\n{command}")

    logger.info("Executing MMAseq")
    status = subprocess.Popen(command, shell=True).wait()

    if status != 0:
        verb = ""
        if verbosity < 1:
            verb = "Rerun command with '--verbosity 1' for more details.\n"
        logger.error(
            "Something went wrong during deployment. "
            f"{verb}"
            "Either way you are welcome to post an issue on our Github."
            
        )
        sys.exit(1)

    else:
        logger.info(
            f"Deployment complete on {dataset} dataset. "
            f"Environments installed and databases downloaded to {deploy_dir}.\n"
            f"Results from Test dataset stored in {outdir}"
        )


def launcher() -> None:

    # Parse user input
    args = parse_deploy()

    # Adjust logger
    adjust_log(logger, args.verbosity)

    deploy(args)

    logger.info("Deployment successful!")

# Initiate logging
logger = initiate_log("MMAdeploy")
import gevent
from locust.env import Environment
from locust.stats import stats_printer, stats_history, StatsCSVFileWriter, PERCENTILES_TO_REPORT
from locust.log import setup_logging
from locust_tasks.tasks import ImageModel
from loguru import logger
import os
from datetime import datetime

from auth.instance_principal_provider import InstancePrincipalProvider
from auth.user_principal_provider import UserPrincipalProvider
from oci_util.casper_data_store import CasperDataStore
from object_uri import ObjectUri
from shutil import make_archive

NUMBER_OF_USERS = int(os.environ.get("NUMBER_OF_USERS", 10))
SPAWN_RATE = int(os.environ.get("SPAWN_RATE", 10))
RUNNING_TIME = int(os.environ.get("RUNNING_TIME", 30))
TEST_CSV_STATS_INTERVAL_WAIT_SEC = 0.2
RPS_SLO = 0
FAILURE_PER_SECONDS_SLO = 5
BUCKET_NAME = os.environ.get("BUCKET_NAME", "load-tests")
PRINCIPAL = os.environ.get("PRINCIPAL", "instance_principal")
RESULT_FOLDER = "output_stats/"
setup_logging("INFO", None)

auth_switcher = {
    "user_principal": UserPrincipalProvider(),
    "instance_principal": InstancePrincipalProvider()
}


def _write_csv_files(environment, stats_base_name, full_history=False):
    stats_writer = StatsCSVFileWriter(
        environment, PERCENTILES_TO_REPORT, stats_base_name, full_history=full_history)
    greenlet = gevent.spawn(stats_writer)
    gevent.sleep(TEST_CSV_STATS_INTERVAL_WAIT_SEC)
    gevent.kill(greenlet)
    stats_writer.close_files()


def _upload_to_casper(source: str, target: str) -> str:
    auth_provider = auth_switcher.get(PRINCIPAL, InstancePrincipalProvider())
    casper_data_store = CasperDataStore(auth_provider)
    namespace = casper_data_store.get_namespace()
    object_locater = ObjectUri.create(namespace, BUCKET_NAME, target)
    casper_data_store.upload(source, object_locater)
    logger.info("{} has been uploaded to {}", source, BUCKET_NAME)


def _get_output_file_path(model_name: str, num_of_users: str):
    output_file_path = None
    if "ic" in model_name:
        output_file_path = f"ic/{num_of_users}-user/"
    elif "od" in model_name:
        output_file_path = f"od/{num_of_users}-user/"
    elif "dc" in model_name:
        output_file_path = f"dc/{num_of_users}-user/"
    elif "ld" in model_name:
        output_file_path = f"ld/{num_of_users}-user/"
    elif "kv" in model_name:
        output_file_path = f"kv/{num_of_users}-user/"
    elif "ocr" in model_name:
        output_file_path = f"ocr/{num_of_users}-user/"
    elif "td" in model_name:
        output_file_path = f"td/{num_of_users}-user/"
    else:
        output_file_path = f"unknown_model/{num_of_users}-user/"
    cur_date = str(datetime.now())
    image_version = os.environ.get("IMAGE_VERSION", "unknown")
    return f"{output_file_path}{cur_date}-{image_version}"


def _get_output_file_name(model_name: str, num_of_users: str):
    output_file_name = None
    if "ic" in model_name:
        output_file_name = "ic"
    elif "od" in model_name:
        output_file_name = "od"
    elif "dc" in model_name:
        output_file_name = "dc"
    elif "ld" in model_name:
        output_file_name = "ld"
    elif "kv" in model_name:
        output_file_name = "kv"
    elif "ocr" in model_name:
        output_file_name = "ocr"
    elif "td" in model_name:
        output_file_name = "td"
    else:
        output_file_name = "unknown_model"
    return f"{output_file_name}-{num_of_users}-user"


def test_loading(num_of_users: int, spawn_rate: int, running_time: int, result_folder: str):
    # setup Environment and Runner
    env = Environment(user_classes=[ImageModel])
    env.create_local_runner()

    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))

    # start a WebUI instance
    env.create_web_ui()

    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    env.runner.start(num_of_users, spawn_rate=spawn_rate)
    logger.info("============= load testing config =============")
    logger.info(f"Number of users: {num_of_users}")
    logger.info(f"Spawn rate: {spawn_rate}")
    logger.info(f"Running time: {running_time} secs")

    # stop the runner after specified time
    gevent.spawn_later(running_time, lambda: env.runner.quit())

    # wait for the greenlets
    env.runner.greenlet.join()

    # stop the web server for good measures
    env.web_ui.stop()

    logger.info("============= load testing result =============")
    logger.info(
        f"95% percentile response time: {env.stats.total.get_response_time_percentile(0.95)}")
    logger.info(f"Average response time: {env.stats.total.avg_response_time}")
    logger.info(f"Total rps: {env.stats.total.total_rps}")
    logger.info(
        f"Total fail per seconds: {env.stats.total.total_fail_per_sec}")

    model_name = os.environ.get("MODEL_NAME")
    output_file_type = "tar"
    output_file_path = _get_output_file_path(
        model_name=model_name, num_of_users=str(num_of_users))
    output_file_name = _get_output_file_name(
        model_name=model_name, num_of_users=str(num_of_users))

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    _write_csv_files(env, result_folder)
    make_archive(output_file_name, output_file_type, result_folder)
    _upload_to_casper(f"{output_file_name}.{output_file_type}",
                      f"{output_file_path}.{output_file_type}")


if __name__ == "__main__":
    test_loading(num_of_users=NUMBER_OF_USERS, spawn_rate=SPAWN_RATE,
                    running_time=RUNNING_TIME, result_folder=f"{NUMBER_OF_USERS}-user/")

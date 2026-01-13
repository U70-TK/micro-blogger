import subprocess
from time import sleep
import consolemenu
from consolemenu.items import *
from pathlib import Path
import shutil
from time import sleep

API_CONTAINER_NAME = "micro_blog_api"

def _apiContainerRunning(print_result=True) -> bool:
    """Determines if the API container is running

    Args:
        print_result (bool, optional): Print if the container is not running. Defaults to True.

    Returns:
        bool: API container running status
    """
    is_running = subprocess.run(f"docker ps", shell=True, capture_output=True, text=True).stdout.find('micro_blog_api') > 0
    if not is_running and print_result: print("Make sure that the api container is running.")
    return is_running


def _apiContainerExecute(command: str) -> None:
    """Executes a command in the API container

    Args:
        command (str): The command to exevute
    """
    subprocess.run(f"docker exec {API_CONTAINER_NAME} {command}", shell=True)


def start() -> None:
    """Starts all needed docker containers
    """

    DIST_PATH = './micro_blog_api/dist'

    # only remove the old dist (ie if the api isn't running and the folder exists)
    if not _apiContainerRunning(print_result=False) and Path(DIST_PATH).is_dir():
        shutil.rmtree(DIST_PATH)

    subprocess.run("docker compose -f ./docker-compose-dev.yaml up -d", shell=True)
    print("Waiting for compilation......")

    # wait until the files are compiled before running the migration
    while not Path('./micro_blog_api/dist/config/typeorm.js').is_file():
        continue

    print("Compilation Complete! Running latest migrations.....")
    sleep(3)
    migrateUp()
    print("Done!")


def stop() -> None:
    """Stops all docker containers
    """
    subprocess.run("docker compose down", shell=True)


def restart() -> None:
    """Restarts all docker containers
    """
    stop()
    start()


def clearCache() -> None:
    """Clears All docker cache
    """
    stop()
    cache_clear_cmds = ['docker container prune', 'docker image prune -a', 'docker builder prune']
    for command in cache_clear_cmds:
        try:
            subprocess.run(f"{command} -f", shell=True, capture_output=True, check=True, text=True)
        except subprocess.CalledProcessError as error:
            print(f"Error (code {error.returncode}): {error.stderr}")

    print("Cache Deleted!")


def newMigration() -> None:
    """Creates A new TypeORM Migration
    """
    if not _apiContainerRunning(): return

    migration_name: str = input("Enter the name of the migration: ")
    CMD = f"npm run typeorm migration:create ./src/migrations/{migration_name}"
    _apiContainerExecute(CMD)
    return


def migrateUp() -> None:
    """Runs all pending migrations
    """
    if not _apiContainerRunning(): return

    CMD = f"npm run migration:run"
    _apiContainerExecute(CMD)
    return


def migrateDown() -> None:
    """Reverts the latest applied migration
    """
    if not _apiContainerRunning(): return

    CMD = f"npm run migration:revert"
    _apiContainerExecute(CMD)
    return


def newController() -> None:
    """Generates a new Nestjs Controller
    """
    if not _apiContainerRunning():
        print("Make sure that the api container is running.")
        return

    controller_name: str = input("Enter the name of the controller: ")
    CMD = f"npx @nestjs/cli g controller ./resources/controllers/{controller_name}"
    _apiContainerExecute(CMD)


def newService() -> None:
    """Generates a new Nestjs Service
    """
    if not _apiContainerRunning():
        print("Make sure that the api container is running.")
        return

    service_name: str = input("Enter the name of the service: ")
    CMD = f"npx @nestjs/cli g service ./resources/services/{service_name}"
    _apiContainerExecute(CMD)


def newModule() -> None:
    """Generates a new Nestjs Module
    """
    if not _apiContainerRunning(): return

    module_name: str = input("Enter the name of the module: ")
    CMD = f"npx @nestjs/cli g module ./resources/modules/{module_name}"
    _apiContainerExecute(CMD)


def newResource() -> None:
    """Generates a new Nestjs Resource
    """
    BASE_PATH = './micro_blog_api/src'
    if not _apiContainerRunning(): return
    resource_name: str = input("Enter the name of the resource: ")
    CMD = f"npx @nestjs/cli g resource ./resources/{resource_name}"
    _apiContainerExecute(CMD)


def updateNpmPackages() -> None:
    """Updates the Npm packages inside of the API container
    """
    if not _apiContainerRunning(): return
    CMD = 'npm ci'
    _apiContainerExecute(CMD)

if __name__ == '__main__':
    PROMPT = "Enter an action: "

    # using parallel lists bc selectio returns index not key
    labels = ['start', 'stop', 'restart', 'update npm packages', 'clear cache', 'new resource', 'new controller', 'new service', 'new module',  'new migration', 'migrate up', 'migrate down', 'exit']
    functions = [start, stop, restart, updateNpmPackages, clearCache, newResource, newController, newService, newModule, newMigration, migrateUp, migrateDown,  exit]

    menu = consolemenu.SelectionMenu(labels,"Select an option", clear_screen=False)

    while True:
        menu.show(show_exit_option=False)
        menu.join()

        selection = menu.selected_option
        functions[selection]()
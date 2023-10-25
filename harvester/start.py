# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import base64
import os.path
import time

import click
import re
import json
import requests
import subprocess
import harvester.run
import harvester.settings
from getpass import getpass


def query(url: str, data: object = None, retries: int = 5, sleep_seconds: float = 3.0, **kwargs) -> object|list:
    while retries > 0:
        try:
            if data is None:
                result = requests.get(url, **kwargs)
                click.echo(f"GET {url} {result.status_code}")
            else:
                result = requests.post(url, data=data, **kwargs)
                click.echo(f"POST {url}; {json.dumps(data)} {result.status_code}")
            if result.status_code >= 400:
                try:
                    raise ConnectionError(result.json())
                except (json.JSONDecodeError, AttributeError, KeyError):
                    raise ConnectionError(f"Unable to connect to {url}")
            return result.json()
        except ConnectionError as e:
            click.echo(f"Unable to connect to {url} -- {e}", err=True)
            retries -= 1
            if retries == 0:
                raise e
            else:
                click.echo(f"Retrying in {sleep_seconds}s ({retries} remaining)", err=True)
                time.sleep(sleep_seconds)


def get_name() -> str:
    return input("Enter a name for your harvester: ")


def append_slash(url: str) -> str:
    if url[-1] != "/":
        url = f"{url}/"
    return url


def get_url() -> str:
    click.echo("Enter the URL for the Galv server you wish to connect to.")
    url = input("API URL: ")
    return append_slash(url)

def create_monitored_path(
        api_url, api_token, harvester_uuid, specified,
        team_id, monitor_path, monitor_path_regex
) -> None:
    click.echo("The harvester will monitor a path on the server for changes and upload files.")
    click.echo(("You must be a Team administrator to create a monitored path. "
                "Note that Lab administrators are not necessarily Team administrators."))

    def monitored_path_exit(error: str):
        click.echo('Harvester successfully created, but the monitored path could not be set.')
        click.echo(f"Error: {error}", err=True)
        click.echo('Please go to the frontend to set a monitored path.')
        click.echo('')

    # To create monitored paths, we must be a team administrator
    teams_administered = []
    try:
        teams = query(f"{api_url}teams/", headers={'Authorization': f"Bearer {api_token}"})
        teams_administered = [t for t in teams['results'] if t['permissions']['write']]
    except BaseException as e:
        return monitored_path_exit(f"Unable to retrieve team list using API key -- {e}")

    # Check team okay
    if team_id is not None and team_id not in [t['id'] for t in teams_administered]:
        return monitored_path_exit(f"Team {team_id} is not administered by this user.")

    page = 0
    page_size = 10
    while team_id is None:
        if len(teams_administered) == 1:
            team_id = teams_administered[0]['id']
            break
        elif specified:
            return monitored_path_exit('You administrate multiple teams and no team is specified with --team_id.')
        teams = teams_administered[page:page + page_size]
        has_prev = page != 0
        has_next = len(teams_administered) > ((page + 1) * page_size)
        click.echo("Press a number for the Team that will own this Harvester.")
        for i, r in enumerate(teams):
            s = f"{i}: {r['name']}"
            click.echo(s)
        if has_prev or has_next:
            p = "[p]revious" if has_prev else ""
            n = "[n]ext" if has_next else ""
            s = f"Or go to the {'/'.join([p, n])} page of results"
            click.echo(s)

        input_char = click.getchar()
        if input_char == "p":
            if not has_prev:
                click.echo("No previous page available to navigate to!")
                continue
            page -= 1
            continue
        if input_char == "n":
            if not has_next:
                click.echo("No next page available to navigate to!")
                continue
            page += 1
            continue

        try:
            input_char = int(input_char)
            assert input_char <= page_size - 1
        except ValueError:
            click.echo(f"Unrecognised option {input_char}")
        except AssertionError:
            click.echo(f"{input_char} is not an available option")

        team_id = teams[input_char]['id']

    team = [t for t in teams_administered if t['id'] == team_id][0]

    # Check path okay
    if monitor_path is None:
        click.echo("Enter a directory on the server to monitor, or leave blank to skip this step.")
        while True:
            monitor_path = input("Path: ")
            if monitor_path == "":
                monitor_path = None
                click.echo("Skipping path monitoring.")
                break
            abs_path = os.path.abspath(monitor_path)
            if monitor_path != abs_path:
                click.echo(f"Using absolute path {abs_path}")
                monitor_path = abs_path
            if not os.path.exists(monitor_path):
                click.echo(f"Path {monitor_path} does not exist.", err=True)
                continue
            if not os.path.isdir(monitor_path):
                click.echo(f"Path {monitor_path} is not a directory.", err=True)
                continue
            regex_ok = monitor_path_regex is not None
            while not regex_ok:
                monitor_path_regex = input(
                    "Enter a regex to match files in this directory to monitor, or leave blank to monitor all files: ")
                if monitor_path_regex == "":
                    monitor_path_regex = ".*"
                    regex_ok = True
                else:
                    try:
                        re.compile(monitor_path_regex)
                        regex_ok = True
                    except re.error as e:
                        click.echo(f"Invalid regex -- {e}", err=True)
            break

    if monitor_path is not None:
        regex_str = f" with regex {monitor_path_regex}" if monitor_path_regex is not None else ""
        click.echo(f"Setting monitor path to {monitor_path}{regex_str}")
        try:
            query(
                f"{api_url}monitored_paths/",
                {
                    'path': monitor_path,
                    'regex': monitor_path_regex,
                    'harvester': harvester_uuid,
                    'team': team['id'],
                },
                headers={
                    'Authorization': f"Bearer {api_token}"
                },
            )
        except BaseException as e:
            return monitored_path_exit(f"Unable to set monitored path -- {e}")


def register(
        url: str = None, name: str = None, api_token: str = None,
        credentials: str = None, lab_id: int = None, team_id: int = None,
        monitor_path: str = None, monitor_path_regex: str = ".*",
        run_foreground: bool = False
):
    """
    Guide a user through the setup process.

    Specifying any of the config args (url, name, api_token, lab_id, monitor_path, monitor_path_regex) function avoid all calls to input() making it non-interactive.
    """
    specified = (
            url is not None or
            name is not None or
            api_token is not None or
            credentials is not None or
            lab_id is not None or
            monitor_path is not None
    )
    # Check we can connect to the API
    if url is not None:
        url = append_slash(url)
    while True:
        if not specified:
            url = get_url()
        try:
            query(f"{url}")
            break
        except BaseException as e:
            click.echo(f"Unable to connect to {url} -- {e}", err=True)
            if specified:
                exit(1)

    # Check token okay
    labs_administered = []
    while True:
        if not specified:
            api_token = input("Enter your API token or leave blank to use username/password authorisation instead: ")
            if api_token == "":
                username = input("Enter your username: ")
                password = getpass()
                credentials = f"{username}:{password}"
        try:
            if api_token is None and credentials is not None:
                try:
                    auth_str = base64.b64encode(bytes(credentials, 'utf-8'))
                    basic_auth = query(
                        f"{url}login/",
                        {},
                        headers={"Authorization": f"Basic {auth_str.decode('utf-8')}"}
                    )
                    api_token = basic_auth['token']
                except BaseException as e:
                    click.echo(f"Unable to authenticate using username/password -- {e}", err=True)
                    if specified:
                        exit(1)
                    continue

            labs = query(f"{url}labs/", headers={'Authorization': f"Bearer {api_token}"})
            labs_administered = [l for l in labs['results'] if l['permissions']['write']]
        except BaseException as e:
            click.echo(f"Unable to retrieve lab list using API key -- {e}", err=True)
            if specified:
                exit(1)
        if len(labs_administered) == 0:
            click.echo("This user does not administer any labs. Please try another API key.", err=True)
            if specified:
                exit(1)
            continue
        break

    # Check lab okay
    if lab_id is not None and lab_id not in [l['id'] for l in labs_administered]:
        click.echo(f"Lab {lab_id} is not administered by this user.", err=True)
        exit(1)

    page = 0
    page_size = 10
    while lab_id is None:
        if len(labs_administered) == 1:
            lab_id = labs_administered[0]['id']
            break
        elif specified:
            click.echo('You administrate multiple labs. Please specify a lab using --lab_id.', err=True)
            exit(1)
        labs = labs_administered[page:page + page_size]
        has_prev = page != 0
        has_next = len(labs_administered) > ((page + 1) * page_size)
        click.echo("Press a number for the Lab that will own this Harvester.")
        for i, r in enumerate(labs):
            s = f"{i}: {r['name']}"
            click.echo(s)
        if has_prev or has_next:
            p = "[p]revious" if has_prev else ""
            n = "[n]ext" if has_next else ""
            s = f"Or go to the {'/'.join([p, n])} page of results"
            click.echo(s)

        input_char = click.getchar()
        if input_char == "p":
            if not has_prev:
                click.echo("No previous page available to navigate to!")
                continue
            page -= 1
            continue
        if input_char == "n":
            if not has_next:
                click.echo("No next page available to navigate to!")
                continue
            page += 1
            continue

        try:
            input_char = int(input_char)
            assert input_char <= page_size - 1
        except ValueError:
            click.echo(f"Unrecognised option {input_char}")
        except AssertionError:
            click.echo(f"{input_char} is not an available option")

        lab_id = labs[input_char]['id']

    lab = [l for l in labs_administered if l['id'] == lab_id][0]

    # Check name okay
    if name is None:
        name = get_name()
    while True:
        result = query(f"{url}harvesters/?name={name}&lab_id={lab_id}")

        if result['count'] > 0:
            click.echo(f"This Lab already has a harvester called {name}.", err=True)
            if specified:
                exit(1)
            click.echo("Please try something else.")
            name = get_name()
        else:
            break

    # Register
    click.echo(f"Registering new harvester {name} to Lab {lab['name']}")
    result = query(
        f"{url}harvesters/",
        {'lab': lab['url'], 'name': name},
        headers={'Authorization': f"Bearer {api_token}"}
    )

    # Save credentials
    file_name = harvester.settings.get_settings_file()
    with open(file_name, 'w+') as f:
        json.dump(result, f)
        click.echo("Details:")
        click.echo(json.dumps(result))
        click.echo(f"Saved to {f.name}")

    click.echo("Success.")
    click.echo("")

    if monitor_path is not None or not specified:
        create_monitored_path(
            api_url=url, api_token=api_token, harvester_uuid=result['uuid'], specified=specified,
            team_id=team_id, monitor_path=monitor_path, monitor_path_regex=monitor_path_regex
        )

    click.echo((
        f"You can configure this harvester's details by visiting the API at "
        f"{url} or going to the frontend."
    ))
    click.echo("")
    click.echo("The harvester will check for updates frequently until you change its polling rate when you update it.")
    click.echo("Launching harvester...")
    if run_foreground:
        harvester.run.run_cycle()
    else:
        subprocess.Popen(["python", "-m", "harvester.run"])
        click.echo(f"Complete. Harvester is running and logging to {harvester.settings.get_logfile()}")


@click.command()
@click.option('--url', type=str, help="API URL to register harvester with.")
@click.option('--name', type=str, help="Name for the harvester.")
@click.option('--api_token', type=str, help="Your API token. You must have admin access to at least one Lab.")
@click.option('--credentials', type=str, help="If provided in the form username:password, will attempt to create an API_token. Enter the special value env to fetch credentials from the environment variables DJANGO_SUPERUSER_USERNAME:DJANGO_SUPERUSER_PASSWORD.")
@click.option('--lab_id', type=int, help="Id of the Lab to assign the Harvester to. Only required if you administrate multiple Labs.")
@click.option('--team_id', type=int, help="Id of the Team to create a Monitored Path for. Only required if you administrate multiple Teams and wish to create a monitored path.")
@click.option('--monitor_path', type=str, help="Path to harvest files from.")
@click.option('--monitor_path_regex', type=str, help="Regex to match files to harvest. Other options can be specified using the frontend.", default=".*")
@click.option(
    '--run_foreground',
    is_flag=True,
    help=(
            "On completion, run the harvester in the foreground "
            "(will not close the thread, useful for Dockerized application)."
    )
)
@click.option(
    '--restart',
    is_flag=True,
    help="Ignore other options and run harvester if config file already exists."
)
def click_wrapper(
        url: str, name: str, api_token: str, credentials: str, lab_id: int, team_id: int,
        monitor_path: str, monitor_path_regex: str,
        run_foreground: bool, restart: bool
):
    if restart:
        click.echo("Attempting to restart harvester.")
        # Check whether a config file already exists, if so, use it
        if harvester.settings.get_setting('url'):
            click.echo("Config file found, restarting harvester.")
            harvester.run.run_cycle()
            return
        else:
            click.echo("No config file found, continuing to setup.")
            click.echo("")

    click.echo("Welcome to Harvester setup.")
    if credentials == 'env':
        credentials = f"{os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')}:{os.getenv('DJANGO_SUPERUSER_PASSWORD')}"
    register(
        url=url, name=name, api_token=api_token, credentials=credentials, lab_id=lab_id, team_id=team_id,
        monitor_path=monitor_path, monitor_path_regex=monitor_path_regex,
        run_foreground=run_foreground
    )


if __name__ == "__main__":
    click_wrapper()

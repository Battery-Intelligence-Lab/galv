# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import click
import re
import json
import requests
import subprocess
import harvester.run
import harvester.settings


def query(url: str, data: object = None) -> object|list:
    if data is None:
        result = requests.get(url)
        click.echo(f"GET {url} {result.status_code}")
    else:
        result = requests.post(url, data=data)
        click.echo(f"POST {url}; {json.dumps(data)} {result.status_code}")
    if result.status_code >= 400:
        try:
            raise ConnectionError(result.json()['error'])
        except (json.JSONDecodeError, AttributeError, KeyError):
            raise ConnectionError(f"Unable to connect to {url}")
    return result.json()


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


def register(url: str = None, name: str = None, user_id: int = None, run_foreground: bool = False):
    """
    Guide a user through the setup process.

    If url, name, and user_id are set, those stages are skipped.
    Specifying both makes the function avoid all calls to input() making it non-interactive.
    """
    # Check we can connect to the API
    if url is not None:
        url = append_slash(url)
        url_specified = True
    else:
        url_specified = False
    while True:
        if not url_specified:
            url = get_url()
        try:
            query(f"{url}")
            break
        except BaseException as e:
            click.echo(f"Unable to connect to {url} -- {e}", err=True)
            if url_specified:
                exit(1)

    # Check name okay
    if name is None:
        name = get_name()
        name_specified = False
    else:
        name_specified = True
    while True:
        result = query(f"{url}harvesters/?name={name}")

        if len(result) > 0:
            click.echo(f"There is already a harvester called {name}.", err=True)
            if name_specified:
                exit(1)
            click.echo("Please try something else.")
            name = get_name()
        else:
            break

    # Select a user to administrate
    if user_id is None:
        user_url = ""
        user_name = ""
        result = query(f"{url}users/")
        page = 0
        page_size = 10
        click.echo("All harvesters require an administrator to complete setup. Fetching users from database...")
        while user_url == "":
            users = result[page:page + page_size]
            has_prev = page != 0
            has_next = len(result) > ((page + 1) * page_size)
            click.echo("Press a number for the username you would like to assign as harvester admin.")
            for i, r in enumerate(users):
                s = f"{i}: {r['username']}"
                click.echo(s)
            if has_prev or has_next:
                p = "[p]revious" if has_prev else ""
                n = "[n]ext" if has_next else ""
                s = f"Or go to the {'/'.join([p, n])} page of results"
                click.echo(s)

            user_id = click.getchar()
            if user_id == "p":
                if not has_prev:
                    click.echo("No previous page available to navigate to!")
                    continue
                page -= 1
                continue
            if user_id == "n":
                if not has_next:
                    click.echo("No next page available to navigate to!")
                    continue
                page += 1
                continue

            try:
                user_id = int(user_id)
                assert user_id <= page_size - 1
            except ValueError:
                click.echo(f"Unrecognised option {user_id}")
            except AssertionError:
                click.echo(f"{user_id} is not an available option")

            user_name = users[user_id]['username']
            user_url = users[user_id]['url']
    else:
        user_url = f"{url}users/{user_id}/"
        try:
            result = query(user_url)
        except BaseException:
            exit(1)
        user_name = result['username']

    # Register
    click.echo(f"Registering new harvester {name}, administrated by {user_name}")
    result = query(f"{url}harvesters/", {'user': user_url, 'name': name})

    # Save credentials
    file_name = harvester.settings.get_settings_file()
    with open(file_name, 'w+') as f:
        json.dump(result, f)
        click.echo("Details:")
        click.echo(json.dumps(result))
        click.echo(f"Saved to {f.name}")

    click.echo("Success.")
    click.echo("")
    click.echo((
        f"You can now configure this harvester's watched paths and other details by visiting the API at "
        f"{url}"
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
@click.option('--user_id', type=int, help="ID of an API user to assign as harvester admin.")
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
def click_wrapper(url: str, name: str, user_id: int, run_foreground: bool, restart: bool):
    if restart and harvester.settings.get_setting('url'):
        harvester.run.run_cycle()
    else:
        register(url=url, name=name, user_id=user_id, run_foreground=run_foreground)


if __name__ == "__main__":
    # Check whether a config file already exists, if so, use it
    click.echo("Welcome to Harvester setup.")
    click_wrapper()

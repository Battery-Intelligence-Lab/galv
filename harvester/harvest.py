import time


def update_config():
    print("Updating configuration from API")


def harvest():
    print("Beginning harvest cycle")


def run():
    update_config()
    harvest()
    time.sleep(10)


def run_cycle():
    while True:
        run()


if __name__ == "main":
    run()

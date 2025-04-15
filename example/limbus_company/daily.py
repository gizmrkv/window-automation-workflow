import threading

from automator import LimbusCompanyAutomator


def battle_loop(automator: LimbusCompanyAutomator):
    while True:
        automator.run_battle()


if __name__ == "__main__":
    auto = LimbusCompanyAutomator("LimbusCompany")
    # battle_thread = threading.Thread(target=battle_loop, args=(auto,))
    # screenshot_thread = threading.Thread(target=auto.run_screenshot)

    # battle_thread.daemon = True
    # screenshot_thread.daemon = True

    # battle_thread.start()
    # screenshot_thread.start()

    # battle_thread.join()
    # screenshot_thread.join()

    auto.run()

import time
from pathlib import Path

import keyboard
from loguru import logger
from PIL import Image

import window_automation_workflow as waw
from window_automation_workflow.utils import is_same_rgb


class LimbusCompanyAutomator(waw.Automator):
    def __init__(
        self,
        title_pattern: str,
        *,
        screenshot_dir: str | Path = "screenshot",
        template_dir: str | Path = "template",
    ):
        super().__init__(
            title_pattern,
            screenshot_dir=screenshot_dir,
        )
        self.template_dir = Path(template_dir)

        self.templates = {
            name.stem: Image.open(name) for name in self.template_dir.glob("*.png")
        }

        self.activate()
        self.resize(1600, 900)
        self.move_window(0, 0)

    def is_home(self) -> bool:
        return self.find_template(self.templates["mirror_menu"]) is not None

    def is_drivers_seat(self) -> bool:
        return self.find_template(self.templates["lightning_entry"]) is not None

    def is_lightning_experience(self) -> bool:
        return self.find_template(
            self.templates["lightning"]
        ) is not None and is_same_rgb(self.pixel(200, 304), (254, 194, 0), tolerance=3)

    def is_lightning_string(self) -> bool:
        return self.find_template(
            self.templates["lightning"]
        ) is not None and is_same_rgb(self.pixel(200, 389), (254, 195, 1), tolerance=3)

    def is_string_entry(self) -> bool:
        return self.find_template(self.templates["entry_string"]) is not None

    def is_formation(self) -> bool:
        return self.find_template(self.templates["information"]) is not None

    def is_turn_start(self) -> bool:
        return self.find_template(self.templates["win_rate_off"]) is not None

    def is_match_ready(self) -> bool:
        return self.find_template(self.templates["match_on"]) is not None

    def is_battle_result(self) -> bool:
        return self.find_template(self.templates["confirm"]) is not None

    def is_no_bonus_rewards(self) -> bool:
        return is_same_rgb(self.pixel(642, 111), (77, 48, 27), tolerance=3)

    def is_empty_enkephalin(self) -> bool:
        return is_same_rgb(self.pixel(405, 833), (34, 20, 8), tolerance=10)

    def is_enkrphalin_making(self) -> bool:
        return self.find_template(self.templates["enkephalin_filling_max"]) is not None

    def is_battle_pass(self) -> bool:
        return (
            self.find_template(self.templates["pass_mission"]) is not None
            and self.find_template(self.templates["limbus_pass"]) is not None
        )

    def is_pass_mission(self) -> bool:
        return (
            self.find_template(self.templates["battle_pass"]) is not None
            and self.find_template(self.templates["daily_mission"]) is not None
        )

    def run(self):
        self.wait_until(self.is_home)
        self.run_module_making()
        self.wait_until(self.is_home)
        self.click_template(self.templates["driver_seat"])
        self.wait_until(self.is_drivers_seat)
        self.click_template(self.templates["lightning_entry"])
        self.wait_until(self.is_lightning_experience)
        self.click(1380, 609)
        self.wait_until(self.is_formation)
        self.click(1426, 742)
        self.run_battle()
        self.wait_until(self.is_lightning_experience)
        self.click_template(self.templates["string"])
        self.run_string()
        self.wait_until(self.is_lightning_string)
        self.click_template(self.templates["back"])
        self.wait_until(self.is_drivers_seat)
        self.click_template(self.templates["glass_window"])
        self.wait_until(self.is_home)
        self.run_receive_pass_reward()

    def run_module_making(self):
        self.wait_until(self.is_home)
        if not self.is_empty_enkephalin():
            self.click(575, 726)
            self.wait_until(self.is_enkrphalin_making)
            self.click_template(self.templates["enkephalin_filling_max"])
            time.sleep(0.5)
            self.click_template(self.templates["enkephalin_filling_confirm"])
            time.sleep(0.5)
            self.click_template(self.templates["cancel"])

    def run_battle(self):
        while True:
            self.move_to(1.0, 1.0)
            logger.info("Waiting for battle result or turn start...")
            self.wait_until(
                lambda: self.is_turn_start() or self.is_battle_result(),
            )
            time.sleep(0.5)
            if self.is_battle_result():
                logger.info("Battle result detected.")
                break

            logger.info("Turn start detected.")
            self.click_template(self.templates["win_rate_off"])
            self.wait_until(self.is_match_ready)
            logger.info("Match ready detected.")
            time.sleep(0.5)
            self.screenshot(self.screenshot_dir)
            self.click_template(self.templates["match_on"])

        self.click_template(self.templates["confirm"])

    def run_string(self):
        while True:
            self.wait_until(self.is_lightning_string)
            if self.is_no_bonus_rewards():
                break
            self.click(467, 610, delay=0.5)
            self.wait_until(self.is_string_entry)
            self.click(799, 613, delay=0.5)
            self.wait_until(self.is_formation)
            self.click(1426, 742, delay=0.5)
            self.run_battle()

    def run_screenshot(self):
        logger.info("Press 'x' to take a screenshot.")
        while True:
            if keyboard.is_pressed("x"):
                self.screenshot(self.screenshot_dir)
                logger.info("Screenshot taken.")

            time.sleep(1.0)

    def run_receive_pass_reward(self):
        self.wait_until(self.is_home)
        self.click(1345, 300)
        self.wait_until(self.is_battle_pass)
        self.click_template(self.templates["pass_mission"])
        self.wait_until(self.is_pass_mission)
        for i, y in enumerate([320, 427, 534, 641, 748]):
            if is_same_rgb(self.pixel(514, y), (72, 36, 16), tolerance=50):
                self.click(659, 297 + i * 107)
                time.sleep(0.5)

        self.click_template(self.templates["back"])

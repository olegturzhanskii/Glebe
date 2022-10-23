import os
from typing import TypeAlias, TypedDict, NamedTuple
from functools import wraps
from webbrowser import open_new_tab
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


driver, action_builder = ..., ...
QUIZLET_LINK = os.getenv('QUIZLET_LINK')
headers = {
    'user-agent': 'Mozilla/5.0'
}


Link: TypeAlias = str


class Challenges(TypedDict):
    challenge: str
    source: Link | None


class Pronunciations(NamedTuple):
    part_of_speech: str
    audio: Link
    transcription: str


def browse_with_change(flag: bool, /):
    def browse(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> None | str:
            global driver, action_builder
            driver = webdriver.Safari()
            driver.maximize_window()
            action_builder = ActionChains(driver)
            if flag:
                driver.get(QUIZLET_LINK)
                action_builder\
                    .click(
                        driver.find_element(
                            By.XPATH,
                            '//*[@id="page"]/div/div[4]/div/p[2]/a[2]'
                        )
                    )\
                    .perform(

                    )
                action_builder\
                    .send_keys_to_element(
                        driver.find_element(
                            By.XPATH,
                            '//*[@id="username"]'
                        ),
                        os.getenv('QUIZLET_LOGIN')
                    ).perform(

                    )
                action_builder\
                    .send_keys_to_element(
                        driver.find_element(
                            By.XPATH,
                            '//*[@id="password"]'
                        ),
                        os.getenv('QUIZLET_PASSWORD')
                    )\
                    .perform(

                    )
                action_builder\
                    .click(
                        driver.find_element(
                            By.XPATH,
                            '//button[@type="submit"]'
                        )
                    )\
                    .perform(

                    )
                sleep(5)
                output = func(*args, **kwargs)
                sleep(5)
                action_builder\
                    .click(
                        driver.find_element(
                            By.XPATH,
                            '//*[@id="SetPageTarget"]/div/div[1]/div[1]/div/div/div/div[3]/button'
                        )
                    )\
                    .perform(

                    )
                WebDriverWait(
                    driver,
                    5
                ).until(
                    expected_conditions.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="setPageSetDetails"]/div[1]/div/div/div/section/div/div[2]/div/div[2]/div/a'
                        )
                    )
                )
            else:
                output = func(*args, **kwargs)
            driver.close()
            return output
        return wrapper
    return browse


def _parse_challenges() -> str:
    url = QUIZLET_LINK[:-4]
    r = requests.get(url, headers=headers)
    if r.ok:
        return r.text
    else:
        return f'Failed to access the current website {url}.'


def get_list_of_challenges() -> Challenges:
    soup = BeautifulSoup(_parse_challenges(), 'lxml')
    matches = soup.find_all(class_="TermText notranslate lang-en")
    challenges = {
        matches[match - 1].text: source if (
                                           source := matches[match].text
                                       ) != '...' else None for match in range(
            1,
            len(
                matches
            ),
            2
        )
    }
    return Challenges(**challenges)


@browse_with_change(False)
def choose_challenge() -> str:
    challenges: Challenges = get_list_of_challenges()
    url = f'https://flippity.net/rp.php?c={",".join(challenges)}&t=Glebe and Olege\'s Speaking Club'
    driver.get(url)
    action_builder\
        .click(
            driver.find_element(
                By.ID,
                'S'
            )
        )\
        .perform(

        )
    WebDriverWait(
        driver,
        5
    ).until(
        expected_conditions.text_to_be_present_in_element(
            parameters := (
                By.ID,
                'spinnerName'
            ),
            ' '
        )
    )
    challenge = driver.find_element(*parameters).text
    if challenges[challenge] is not None:
        open_new_tab(challenges[challenge])
    return challenge


@browse_with_change(True)
def delete_challenge(challenge: str) -> None:
    element = driver.find_element(
        By.XPATH,
        f'//p[text()="{challenge}"]/ancestor::div[@class="TermContent-inner-padding"]/parent::div/descendant::button['
        '@aria-label="Delete this card"]'
    )
    element.location_once_scrolled_into_view
    element.click()


@browse_with_change(True)
def add_challenge(challenge: str, source: Link | str) -> None:
    element = driver.find_element(By.XPATH, '//*[@id="addRow"]/span/button')
    element.location_once_scrolled_into_view
    element.click()
    driver.switch_to.active_element.send_keys(challenge)
    action_builder\
        .send_keys_to_element(
            driver.find_element(
                By.XPATH,
                f'//p[text()="{challenge}"]/ancestor::div[@class="TermContent-side TermContent-side--word"]/following-'
                'sibling::div/descendant::p'
            ),
            source
        )\
        .perform(

        )


def cambridge_word(word: str) -> None:
    url = f'https://dictionary.cambridge.org/dictionary/essential-american-english/{word}'
    open_new_tab(url)


def _parse_word(word: str) -> str:
    url = f'https://dictionary.cambridge.org/dictionary/essential-american-english/{word}'
    r = requests.get(url, headers=headers)
    if r.ok:
        return r.text
    else:
        return f'Failed to access the current website {url}.'


def pronounce_word(word: str) -> list[Pronunciations, ...] | list:
    soup = BeautifulSoup(_parse_word(word), 'lxml')
    matches = soup.find_all(class_="pos-header dpos-h")
    pronunciations = []
    for match in matches:
        try:
            audio = f'https://dictionary.cambridge.org/us{match.find(type="audio/mpeg")["src"]}'
            part_of_speech = match.find(class_='pos dpos').text
            transcription = match.find(class_="ipa dipa").text
        except (ValueError, TypeError):
            continue
        pronunciations.append(Pronunciations(part_of_speech, audio, transcription))
    return pronunciations


if __name__ == '__main__':
    print(get_list_of_challenges())

import time
import cookie

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

class PersonInfo():
    def __init__(self):
        self.is_private  = False
        self.n_followers = 0
        self.n_following = 0

def fetch(people_type, account, max_people, driver: webdriver.Chrome):
    driver.get(f"https://www.instagram.com/{account}/{people_type}/")

    cookie.load(driver)

    time.sleep(5)

    try:
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'Not Now')]")
        element.click()
    except:
        pass

    followers_div = driver.find_element(By.CLASS_NAME, "_aano")

    time.sleep(3)

    scroll_origin = ScrollOrigin.from_element(followers_div)

    prev_num_of_followers = 0
    while True:
        ActionChains(driver=driver).scroll_from_origin(scroll_origin=scroll_origin, delta_x=0, delta_y=5000).perform()
        time.sleep(10)

        followers_elem = followers_div.find_elements(By.TAG_NAME, "a")

        if len(followers_elem) > max_people:
            print("Max number of followers are reached.")
            break

        if prev_num_of_followers == len(followers_elem):
            print("There are no more followers to fetch")
            break

        prev_num_of_followers = len(followers_elem)

    followers = []

    for follower_elem in followers_elem:
        if len(follower_elem.text) == 0:
            continue

        followers.append(follower_elem.text)

    return followers

def follow_person_with_criteria(account, criteria, driver: webdriver.Chrome):
    driver.get(f"https://www.instagram.com/{account}")

    cookie.load(driver)

    time.sleep(10)

    person = PersonInfo()

    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'This account is private')]")
        person.is_private = True
    except:
        pass

    try:
        n_followers_container = driver.find_element(By.XPATH, "//*[contains(text(), 'followers')]")
        n_following_container = driver.find_element(By.XPATH, "//*[contains(text(), 'following')]")
        
        n_followers_elem = n_followers_container.find_element(By.TAG_NAME, "span")
        n_following_elem = n_following_container.find_element(By.TAG_NAME, "span")
        person.n_followers = int(n_followers_elem.text.replace(',',''))
        person.n_following = int(n_following_elem.text.replace(',', ''))
    except:
        pass

    if criteria(person):
        try:
            follow_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Follow')]")

            follow_button.click()

            print(f'Followed {account}, following: {person.n_following}, followers: {person.n_followers}, private: {person.is_private}')

            time.sleep(4)
        except:
            pass

    return person

def login(driver: webdriver.Chrome):
    driver.get("https://www.instagram.com")

    time.sleep(25)

    cookie.save(driver)
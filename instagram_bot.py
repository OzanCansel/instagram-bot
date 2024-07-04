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
        self.n_posts     = 0

def fetch(people_type, account, max_people, existing_followers: list, driver: webdriver.Chrome):
    driver.get(f"https://www.instagram.com/{account}/{people_type}/")

    time.sleep(5)

    try:
        element = driver.find_element(By.XPATH, f"//*[contains(text(), '{people_type}')]")
        element.click()
    except:
        pass

    time.sleep(10)

    try:
        followers_div = driver.find_element(By.CLASS_NAME, "xyi19xy")
    except:
        return []

    time.sleep(3)

    scroll_origin = ScrollOrigin.from_element(followers_div)

    followers = []
    while True:
        try:
            time.sleep(10)

            followers_elem = followers_div.find_elements(By.TAG_NAME, "a")

            before = len(followers)
            for follower_elem in followers_elem:
                if len(follower_elem.text) == 0:
                    continue

                person = follower_elem.text

                if followers.count(person) > 0:
                    continue

                if not existing_followers.count(follower_elem.text):
                    followers.append(follower_elem.text)
                else:
                    print(f"{person} already contained in the existing followers, so leaving.")
                    return followers

            after = len(followers)

            if len(followers) > max_people:
                print(f"Max number of followers are reached for {account}.")
                break

            if before == after:
                print("There are no more followers to fetch")
                break

            ActionChains(driver=driver).scroll_from_origin(scroll_origin=scroll_origin, delta_x=0, delta_y=5000).perform()
        except Exception as e:
            print(e)
            break

    return followers

def follow_person_with_criteria(account, criteria, ignored_names: list, driver: webdriver.Chrome):
    driver.get(f"https://www.instagram.com/{account}")

    person = PersonInfo()

    time.sleep(30)

    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'This account is private')]")
        person.is_private = True
    except:
        pass

    try:
        user_description = driver.find_element(By.CLASS_NAME, "x7a106z").text
        tokens = user_description.split()

        if len(tokens) > 0:
            first_name =  tokens[0].lower()

            for ignored_name in ignored_names:
                if first_name.startswith(ignored_name):
                    return False
    except:
        pass

    try:
        try:
            n_followers_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'followers')]").find_element(By.TAG_NAME, "span")
        except:
            n_followers_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'follower')]").find_element(By.TAG_NAME, "span")

        n_following_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'following')]").find_element(By.TAG_NAME, "span")

        try:
            n_posts_elem     = driver.find_element(By.XPATH, "//*[contains(text(), 'posts')]").find_element(By.TAG_NAME, "span")
        except:
            n_posts_elem     = driver.find_element(By.XPATH, "//*[contains(text(), 'post')]").find_element(By.TAG_NAME, "span")

        person.n_followers = int(n_followers_elem.text.replace(',', '').replace('.','').replace('M','').replace('K',''))
        person.n_following = int(n_following_elem.text.replace(',', '').replace('.','').replace('M','').replace('K',''))
        person.n_posts     = int(n_posts_elem.text.replace(',', '').replace('.','').replace('M','').replace('K',''))
    except:
        pass

    if criteria(person):
        try:
            follow_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Follow')]")

            follow_button.click()

            print(f'Followed {account}, following: {person.n_following}, followers: {person.n_followers}, private: {person.is_private}')

            time.sleep(6)

            return True
        except:
            pass

    return False

def login(driver: webdriver.Chrome):
    driver.get("https://www.instagram.com")

    time.sleep(25)

    cookie.save(driver)
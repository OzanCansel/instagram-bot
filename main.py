import argparse
import instagram_bot
import os
import random
import cookie
import math

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def create_parser():
    parser = argparse.ArgumentParser(
        prog        = "fetch-followers",
        description = "Exports followers to the file"
    )

    parser.add_argument(
        "--account",
        help="Account which of followers are extracted"
    )
    parser.add_argument(
        "--max_people",
        type=int,
        default=200,
        help="Fetches until number of max_people"
    )
    parser.add_argument(
        "--program",
        required=True,
        default="fetch-people",
        help="Specify the program"
    )
    parser.add_argument(
        "--followers",
        action="store_true"
    )
    parser.add_argument(
        "--following",
        action="store_true"
    )
    parser.add_argument(
        "--input_list",
        help="Path to auto follow list txt"
    )
    parser.add_argument(
        "--pages",
        nargs="*",
        default=[],
        help="Pages to stalk"
    )

    return parser

def write_to(path, list):
    with open(file=path, mode="w") as exported_file:
        print(f"Writing to '{path}'")
        exported_file.writelines('\n'.join(list))

def read_input_list(path):
    if not os.path.exists(path):
        return list()

    with open(file=path, mode="r") as file:
        return file.read().splitlines()

def append_ln(text, path):
    with open(file=path, mode="a") as file:
        file.write(text + "\n")

def follow_criteria(info: instagram_bot.PersonInfo):
    if info.n_followers == 0 or info.n_following == 0:
        return False

    follow_ratio = (info.n_followers / info.n_following)

    return  info.is_private and \
            follow_ratio < 2.1 and \
            follow_ratio > 0.5 and \
            info.n_followers > 100 and \
            info.n_following > 100 and \
            info.n_followers < 1200 and \
            info.n_posts >= 5

def followers_fp(account):
    return f"{account}/followers"

def inspected_fp(account):
    return f"{account}/inspected"

def request_sent_file_path(account):
    return f"{account}/request_sent_file_path"

if __name__ == "__main__":
    args = create_parser().parse_args()

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service)

    if args.program == "diff-people":
        account    = args.account
        max_people = args.max_people

        followers = instagram_bot.fetch(
            people_type = "followers",
            account     = account,
            max_people  = max_people,
            driver      = driver
        )
        following = instagram_bot.fetch(
            people_type = "following",
            account     = account,
            max_people  = max_people,
            driver      = driver
        )

        followers = sorted(followers)
        following = sorted(following)

        people_dont_follow_you = list(set(following) - set(followers))
        people_you_dont_follow = list(set(followers) - set(following))

        write_to(f"{account}_people_dont_follow_you.txt", people_dont_follow_you)

        print("People dont follow you:")
        print("=======================")
        print('\n'.join(people_dont_follow_you))
    elif args.program == "smart-follow":
        pages             = read_input_list("targetpages.txt")
        remaining_pages   = len(pages)
        n_max_people      = 1000

        driver.get("https://www.instagram.com")
        cookie.load(driver)
        random.seed()
        random.shuffle(pages)

        print(pages)

        ignored_names = read_input_list("ignored-names.txt")

        ignored_names_lower = []

        for ignored_name in ignored_names:
            ignored_names_lower.append(ignored_name.lower())

        inspected_followers = []
        for page in pages:
            inspected_followers.extend(read_input_list(inspected_fp(account=page)))

        n_inspected_people = 0
        for page in pages:
            os.makedirs(name=page, exist_ok=True)
            existing_followers = read_input_list(followers_fp(account=page))

            print(f"Fetching followers of {page}")
            followers = instagram_bot.fetch(
                people_type        = "followers",
                account            = page,
                max_people         = n_max_people,
                existing_followers = existing_followers,
                driver             = driver
            )

            for follower in followers:
                append_ln(follower, f"{followers_fp(account=page)}")

            followers = read_input_list(followers_fp(account=page))

            for follower in followers:
                inspected = inspected_followers.count(follower) > 0

                if inspected:
                    continue

                try:
                    if instagram_bot.follow_person_with_criteria(
                        account=follower,
                        criteria=follow_criteria,
                        ignored_names=ignored_names_lower,
                        driver=driver
                    ):
                        append_ln(follower, f"{page}/followed")
                except Exception as e:
                    print(e)
                    print("Instagram request rate is reached, exiting...")
                    exit(0)

                append_ln(follower, inspected_fp(account=page))
                inspected_followers.append(follower)

                n_inspected_people += 1

                if n_inspected_people >= n_max_people:
                    print(f"{n_inspected_people} of people inspected, so exiting.")
                    exit(0)

    elif args.program == "login":
        instagram_bot.login(driver=driver)


    driver.quit()
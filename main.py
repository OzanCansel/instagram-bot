import argparse
import instagram_bot

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

    return parser

def write_to(path, list):
    with open(file=path, mode="w") as exported_file:
        print(f"Writing to '{path}'")
        exported_file.writelines('\n'.join(list))

def read_input_list(path):
    with open(file=path, mode="r") as file:
        return file.read().splitlines()
    
def follow_criteria(info: instagram_bot.PersonInfo):
    if info.n_followers == 0 or info.n_following == 0:
        return False

    follow_ratio = (info.n_followers / info.n_following)

    return  info.is_private and \
            follow_ratio < 3.1 and \
            follow_ratio > 0.3 and \
            info.n_followers > 25 and \
            info.n_following > 25 and \
            info.n_followers < 1000

if __name__ == "__main__":
    args = create_parser().parse_args()

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service)

    if args.program == "fetch-people":
        account       = args.account
        max_people    = args.max_people
        people_type   = "followers"

        if args.following:
            people_type = "following"

        people = instagram_bot.fetch(
            people_type=people_type,
            account=account,
            max_people=max_people,
            driver=driver
        )

        write_to(f'{account}_{people_type}.txt', people)
    elif args.program == "diff-people":
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
    elif args.program == "auto-follow":
        people = read_input_list(args.input_list)

        for person in people:
            instagram_bot.follow_person_with_criteria(
                account=person,
                criteria=follow_criteria,
                driver=driver
            )

    elif args.program == "login":
        instagram_bot.login(driver=driver)


    driver.quit()
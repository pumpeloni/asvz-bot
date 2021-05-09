#!/usr/bin/python3

"""
Based on initial script of Julian Stiefel
Initally Created on: Mar 20, 2019
Author: Julian Stiefel
License: BSD 3-Clause
Description: Script for automatic enrollment in ASVZ classes

Updated Version on: September 25, 2020
Author: Florian Bütler

Updated Version on: November 13, 2020
Author: Marc Zünd
"""

### THIS VERSION USES CHROMIUM AS BROWSER ###

import time
import argparse
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from validators import ValidationFailure, url as url_validator

TIMEFORMAT = "%H:%M"

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def waiting_fct(enrollment_time):
    current_time = datetime.today()

    logging.info(
        "\n\tcurrent time: {}\n\tenrollment starts at: {}".format(
            current_time.strftime("%H:%M:%S"), enrollment_time.strftime("%H:%M:%S")
        )
    )

    login_before_enrollment_seconds = 1 * 60
    if (enrollment_time - current_time).seconds > login_before_enrollment_seconds:
        sleep_time = (
            enrollment_time - current_time
        ).seconds - login_before_enrollment_seconds
        logging.info(
            "Sleep for {} seconds until {}".format(
                sleep_time,
                (current_time + timedelta(seconds=sleep_time)),
            )
        )
        time.sleep(sleep_time)

    return


def asvz_enroll(
    username, password, weekday, facility, enrollment_time, sportfahrplan_link
):
    logging.info("Enrollment started")

    logging.info(
        "\n\tweekday: {}\n\tenrollment time: {}\n\tfacility: {}\n\tsportfahrplan: {}".format(
            weekday, enrollment_time, facility, sportfahrplan_link
        )
    )

    options = Options()
    options.add_argument(
        "--private"
    )  # open in private mode to avoid different login scenario
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(sportfahrplan_link)
        driver.implicitly_wait(10)
        logging.info("Headless Chrome started")

        day_ele = driver.find_element_by_xpath(
            "//div[@class='teaser-list-calendar__day'][contains(., '{}')]".format(
                weekday
            )
        )
        day_ele.find_element_by_xpath(
            ".//li[@class='btn-hover-parent'][contains(., '{}')][contains(., '{}')]".format(
                facility, enrollment_time.strftime(TIMEFORMAT)
            )
        ).click()

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[@class='btn btn--block btn--icon relative btn--primary-border' or @class='btn btn--block btn--icon relative btn--primary']")
            )
        ).click()

        time.sleep(2)  # necessary because tab needs to be open to get window handles
        tabs = driver.window_handles
        driver.switch_to.window(tabs[-1])
        logging.info("Lesson found")

        full = None
        try:
            full = driver.find_element_by_xpath(
                "//alert[@class='ng-star-inserted'][contains(., 'ausgebucht')]"
            )
        except:
            pass
        if full is not None:
            logging.info("Lesson is booked out.")
            return

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@class='btn btn-default ng-star-inserted' and @title='Login']",
                )
            )
        ).click()
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@class='btn btn-warning btn-block' and @title='SwitchAai Account Login']",
                )
            )
        ).click()

        # choose organization:
        organization = driver.find_element_by_xpath(
            "//input[@id='userIdPSelection_iddtext']"
        )
        organization.send_keys("{}a".format(Keys.CONTROL))
        organization.send_keys("ETH Zurich")
        organization.send_keys(Keys.ENTER)

        driver.find_element_by_xpath("//input[@id='username']").send_keys(username)
        driver.find_element_by_xpath("//input[@id='password']").send_keys(password)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        logging.info("Submitted Login Credentials")

        logging.info("Waiting for enrollment")
        WebDriverWait(driver, 5 * 60).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@id='btnRegister' and @class='btn-primary btn enrollmentPlacePadding ng-star-inserted']",
                )
            )
        ).click()
        time.sleep(5)
        logging.info("Successfully enrolled. Bau Chicka Bauwau!")
    finally:
        driver.quit()


def main():
    logging.debug("Parsing arguments")
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="ETHZ username i.e. nethz")
    parser.add_argument("-p", "--password", help="ETHZ password")
    parser.add_argument(
        "-w",
        "--weekday",
        help="Day of the week of the lesson i.e. 0-6 for Monday-Sunday",
    )
    parser.add_argument("-t", "--time", help="Time when the lesson starts e.g. '19:15'")
    parser.add_argument("-e", "--enrollemnt_time_difference",
        help="number of hours in between start of enrollment and start of the event")
    parser.add_argument(
        "-f",
        "--facility",
        help="Facility where the lesson takes place e.g. 'Sport Center Polyterrasse'",
    )
    parser.add_argument(
        "sportfahrplan",
        help="link to particular sport on ASVZ Sportfahrplan, e.g. https://asvz.ch/426-sportfahrplan?f[0]=sport:45743 for volleyball. Make sure there starts only one lesson for that particular time at that particular location (i.e. use ASVZ filters).",
    )
    args = parser.parse_args()
    logging.debug("Parsed arguments")

    # validate args
    if args.weekday == "0":
        weekday = "Montag"
        weekday_nr = 0
    elif args.weekday == "1":
        weekday = "Dienstag"
        weekday_nr = 1
    elif args.weekday == "2":
        weekday = "Mittwoch"
        weekday_nr = 2
    elif args.weekday == "3":
        weekday = "Donnerstag"
        weekday_nr = 3
    elif args.weekday == "4":
        weekday_nr = 4
        weekday = "Freitag"
    elif args.weekday == "5":
        weekday = "Samstag"
        weekday_nr = 5
    elif args.weekday == "6":
        weekday = "Sonntag"
        weekday_nr = 6
    else:
        logging.error("invalid weekday specified")
        exit(1)

    try:
        start_time = datetime.strptime(args.time, TIMEFORMAT)
    except ValueError:
        logging.error("invalid time specified")
        exit(1)

    enrollemnt_time_difference = int(args.enrollemnt_time_difference)
    if not(enrollemnt_time_difference >= 1) and not(24 >= enrollemnt_time_difference):
        logging.error("invalid enrollment time specified")
        exit(1)


    if not url_validator(args.sportfahrplan):
        logging.error("invalid url specified")
        exit(1)

    #constructing enrollemnt date and time

    current_time = datetime.today()

    start_time = datetime(
        current_time.year,
        current_time.month,
        current_time.day,
        start_time.hour,
        start_time.minute,
    )

    while start_time.weekday() != weekday_nr:
        start_time += timedelta(days=1)

    #constucting link with time filter

    if(start_time.hour >= 10):
        plan_hour = str(start_time.hour)
    else:
        plan_hour = "0" + str(start_time.hour)

    if(start_time.minute >= 10):
        plan_min = str(start_time.minute)
    else:
        plan_min = "0" + str(start_time.minute)

    if(start_time.day >= 10):
        plan_day = str(start_time.day)
    else:
        plan_day = "0" + str(start_time.day)

    if(start_time.hour >= 10):
        plan_month = str(start_time.month)
    else:
        plan_month = "0" + str(start_time.month)

    sportfahrplan_mit_zeitfilter = args.sportfahrplan + "&date=" + str(start_time.year) + "-" + plan_month + "-" + plan_day + "%20" + plan_hour + ":" + plan_min

    #constructing enrollment start time
    enrollment_start_time = start_time
    enrollment_start_time -= timedelta(hours=enrollemnt_time_difference)

    logging.info("Script started")
    waiting_fct(enrollment_start_time)


    asvz_enroll(
        args.username,
        args.password,
        weekday,
        args.facility,
        start_time,
        sportfahrplan_mit_zeitfilter,
    )
    logging.info("Script successfully finished")


if __name__ == "__main__":
    main()

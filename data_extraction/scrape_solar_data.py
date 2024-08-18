
# import the required libraries
import os
import pickle
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# Wait for the overlay to disappear
from selenium.common.exceptions import NoSuchElementException
#

import numpy as np
from haversine import haversine, Unit
import requests


# read stops file from network
network = 'Canberra_1.7k'
stops = pd.read_csv(f'./{network}/stops.txt')
trips = pd.read_csv(f'./{network}/trips.txt')
# calendar = pd.read_csv(f'./{network}/calendar.txt')
# routes = pd.read_csv(f'./{network}/routes.txt')
# group the trips by service_id and number of trips
trips_grouped = trips.groupby(['service_id']).agg({'trip_id': 'count'}).reset_index()
# trips_study = trips[trips['service_id'] == "LA"]
stop_times = pd.read_csv(f'./{network}/stop_times.txt')
# filter stop times based on the trips
stop_times = stop_times[stop_times['trip_id'].isin(trips['trip_id'])]
# find the terminal stops
terminal_stops_ = stop_times.groupby('trip_id').agg({'stop_id': ['first', 'last']}).reset_index()
# take unique of start and last stop
terminal_stops = set(terminal_stops_[('stop_id', 'first')].unique()).union(set(terminal_stops_[('stop_id', 'last')].unique()))
# terminal_stops = [3419]
stops = stops[stops['stop_id'].isin(terminal_stops)]

# C:\Users\Cistup\Downloads\solar_data find the files in this folder
# folder_path = r'C:/Users/Cistup/Downloads/solar_data'
# files = os.listdir(folder_path)
# stops_done = []
# for file in files:
#     if file[:3] in terminal_stops:
#         stops_done.append(file[:3])
#
# stops_needed = terminal_stops - set(stops_done)
#
# stops = stops[stops['stop_id'].isin(stops_needed)]

for index, row in stops.iterrows():
    print(index)
    # get the lat and lon
    lat = row['stop_lat']
    lon = row['stop_lon']
    # specify the url
    url = f"https://pvwatts.nrel.gov/pvwatts.php"

    from selenium import webdriver
    from bs4 import BeautifulSoup

    # Start a new instance of Chrome web browser
    driver = webdriver.Chrome()

    # Load the webpage
    driver.get(url)

    # Wait for the content to be fully loaded
    wait = WebDriverWait(driver, 20) # Wait for 10 seconds (adjust as needed)

    # Assuming 'driver' is your WebDriver object
    wait.until(EC.presence_of_element_located((By.ID, 'myloc2')))
    # send the latitude and longitude
    try:
        element = driver.find_element(By.XPATH, '//*[@id="myloc2"]')
        element.send_keys(f"{lat}, {lon}")
    except Exception as e:
        element = driver.find_element(By.XPATH, '//*[@id="myloc2"]')
        element.send_keys(f"{lat}, {lon}")
    driver.implicitly_wait(10)
    # click on the submit button
    wait.until(EC.presence_of_element_located((By.ID, 'go2')))
    try:
        element = driver.find_element(By.XPATH, '//*[@id="go2"]')
    except Exception as e:
        element = driver.find_element(By.XPATH, '//*[@id="go2"]')
    # click on the submit button
    element.click()
    try:
        WebDriverWait(driver, 10).until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, '.ui-widget-overlay')))
    except NoSuchElementException:
        pass
    wait.until(EC.presence_of_element_located((By.ID, 'directright')))
    try:
        # find element with id = 'directright'
        element = driver.find_element(By.XPATH, '//*[@id="directright"]')
    except Exception as e:
        # find element with id = 'directright'
        element = driver.find_element(By.XPATH, '//*[@id="directright"]')
    # click on the submit button
    element.click()
    wait.until(EC.presence_of_element_located((By.ID, 'system_capacity')))
    try:
        # find element with id = 'system_capacity'
        element = driver.find_element(By.XPATH, '//*[@id="system_capacity"]')
    except Exception as e:
        # find element with id = 'system_capacity'
        element = driver.find_element(By.XPATH, '//*[@id="system_capacity"]')
    # replace the existing value with 1
    element.clear()
    # send the value 1
    try:
        element.send_keys("0.16")
    except Exception as e:
        element.send_keys('0.16')
    driver.implicitly_wait(2)
    wait.until(EC.presence_of_element_located((By.ID, 'tilt')))
    try:
        # find element with id = 'tilt'
        element = driver.find_element(By.XPATH, '//*[@id="tilt"]')
    except Exception as e:
        # find element with id = 'tilt'
        element = driver.find_element(By.XPATH, '//*[@id="tilt"]')
    # replace the existing value with 1
    element.clear()
    # send the latitude value
    try:
        element.send_keys(f"{lat}")
    except Exception as e:
        element.send_keys(f"{lat}")

    try:
        wait.until(EC.presence_of_element_located((By.ID, 'arrowright')))
        # find element with id = 'arrowright'
        element = driver.find_element(By.XPATH, '//*[@id="arrowright"]')
    except Exception as e:
        wait.until(EC.presence_of_element_located((By.ID, 'arrowright')))
        # find element with id = 'arrowright'
        element = driver.find_element(By.XPATH, '//*[@id="arrowright"]')
    # click on the submit button
    element.click()
    driver.implicitly_wait(10)
    # wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.pvGevent[href="download_results.php?type=hourly"]')))
    # find element with //*[@id="exportresults"]/a[3]
    # element = driver.find_element(By.XPATH, '//*[@id="exportresults"]/a[3]')
    # element = driver.find_element(By.CSS_SELECTOR, 'a.pvGevent[href="download_results.php?type=hourly"]')
    try:
        element = driver.find_element(By.XPATH, '//*[@id="exportresults"]/a[3]')
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        element = driver.find_element(By.XPATH, '//*[@id="exportresults"]/a[3]')
        driver.execute_script("arguments[0].click();", element)

    element.click()

    # close the browser
    driver.quit()

    # go to download folder and read the file named pv_watts_hourly.csv
    # change the name of the file to the {stop}_{lat}_{lon}.csv
    folder_path = r'C:/Users/Cistup/Downloads'
    files = os.listdir(folder_path)
    # rename the file
    for file in files:
        if file.startswith('pvwatts_hourly'):
            # print(file)
            os.rename(f'{folder_path}/{file}', f'{folder_path}/{row["stop_id"]}_{lat}_{lon}.csv')
            # locate the file in different folder
            os.replace(f'{folder_path}/{row["stop_id"]}_{lat}_{lon}.csv', f'{folder_path}/solar_data/{row["stop_id"]}_{lat}_{lon}.csv')
            break




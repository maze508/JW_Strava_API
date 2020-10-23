from selenium import webdriver
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule
import time
from env import *


# Main Function
def main():
    # Finds the driver location (For Selenium)
    # Add Headless Options to prevent Chrome Browser from Opening whenever it runs 
    #! NOTE : Did not specifically go into running Selenium on Batch Files. Seems a little too complicated for project scale.
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    # Init Driver
    driver = webdriver.Chrome(executable_path = PATH_TO_CHROME_DRIVER, chrome_options=options)

    # API Request URL
    driver.get(LEADERBOARDS_WEBSITE)


    # Finds the Table Headers
    table_headers = []
    for items in driver.find_elements_by_xpath("//div[@class='leaderboard']/table/thead//th"):
        table_headers.append(items.text)

    # Defining Arrays/Lists Used later on
    table_rows = []
    myrow = []
    master_list = []
    rank_list = []
    name_list = []
    distance_list = []
    runs_list = []
    longest_list = []
    avg_pace_list = []
    elev_gain_list = []

    # Finds the Total Rows present in the table 
    totalrows = len(driver.find_elements_by_xpath("//div[@class='leaderboard']/table/tbody//tr"))

    # Finds the Contents every consecutive table row of the specific table
    for i in range(totalrows):
        myrow.clear()
        for items in driver.find_elements_by_xpath("//div[@class='leaderboard']/table/tbody//tr["+str(i+1)+"]/td"):
            myrow.append(items.text)

        # Adds content to Master List
        master_list.extend(myrow)

    # Quit driver before post processing to save RAM D;
    driver.quit()

    # Filters data and sorts it
    for i, x in enumerate(master_list):
        if i == 0 or i % 7 == 0:
            rank_list.append(x)
        elif i == 1 or (i-1) % 7 == 0:
            name_list.append(x)
        elif i == 2 or (i-2) % 7 == 0:
            distance_list.append(x)
        elif i == 3 or (i-3) % 7 == 0:
            runs_list.append(x)
        elif i == 4 or (i-4) % 7 == 0:
            longest_list.append(x)
        elif i == 5 or (i-5) % 7 == 0:
            avg_pace_list.append(x)
        elif i == 6 or (i-6) % 7 == 0:
            elev_gain_list.append(x)

    # Pack all the data into a pd Dataframe for exporting
    df = pd.DataFrame(
        {
            'Rank': rank_list,
            'Athlete': name_list,
            'Distance': distance_list,
            'Runs': runs_list,
            'Longest': longest_list,
            'Avg. Pace': avg_pace_list,
            'Elev. Gain': elev_gain_list
        }
    )

    # Exports data to a .csv file for backup
    #! Optional (Maybe good to safe just in case)
    df.to_csv(LOCATION_TO_DOWNLOAD_CSV, index=False)

    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Read User credentials for API key
    creds = ServiceAccountCredentials.from_json_keyfile_name(NAME_OF_JSON_FILE, scope)

    # Authorise user
    client = gspread.authorize(creds)

    # Uploads the sheet to the first sheet (sheet1) of "Strava" Google Sheets
    worksheet = client.open(NAME_OF_GOOGLE_SHEET).sheet1

    # Auto Updates the Google Sheets
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print('Uploaded to Google Sheets')


# Runs the Script Immediately when clicked
main()

# Runs Script Every (User Defined) Minute(s)
schedule.every(UPLOAD_TO_GOOGLE_SHEETS_INTERVAL_MINUTES).minutes.do(main)
print('~~~~~~~~~~~~~~~~~~~~~~~')
print()
print('~~~~~~~~~~~~~~~~~~~~~~~')

while True:
    schedule.run_pending()
    time.sleep(1)
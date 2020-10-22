from selenium import webdriver
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule
import time


# Main Function
def main():
    # Finds the driver location (For Selenium)
    #* TO Download Chrome Driver :
        # Go to `https://sites.google.com/a/chromium.org/chromedriver/`
        # Down load "Latest stable release: ChromeDriver 86.0.4240.22"
        # Find its path and change the paths under executable path)
    # Add Headless Options to prevent Chrome Browser from Opening whenever it runs 
    #! NOTE : Did not specifically go into running Selenium on Batch Files. Seems a little too complicated for project scale. Can explore for "easier" user experience
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(executable_path = r"C:\Users\Admin\Documents\chromedriver.exe", chrome_options=options)

    # API Request URL
    driver.get('https://www.strava.com/clubs/midswing')

    # Find the Search Button and return the specified search results

    # Finds the Table Headers
    table_headers = []
    for items in driver.find_elements_by_xpath("//div[@class='leaderboard']/table/thead//th"):
        table_headers.append(items.text)

    # Defining Arrays Used later on
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

        # Master List
        master_list.extend(myrow)

    driver.quit()

    # Filters the data and sorts in
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

    # Stuff all the data into the dataframe to be exported
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

    # Exports data to csv and saves as backup
    #! Optional (Maybe good to safe just in case)
    df.to_csv(r"C:\Users\Admin\Desktop\Work\Jiaweis_API\strava_leaderboards.csv", index=False)


    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # READ ME REFER TO `https://www.youtube.com/watch?v=w533wJuilao`
    #! Note that Sharing should untick Notify me box
    #! Note that should enable both google sheets and google docs api

    # Read User credentials for API key
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

    # Authorise user
    client = gspread.authorize(creds)

    # Uploads the sheet to the first sheet (sheet1) of "Strava" Google Sheets
    worksheet = client.open("Strava").sheet1

    # Auto Updates the Google Sheets
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print('Uploaded to Google Sheets')


# Runs the Script Immediately when clicked
main()

# Runs Script Every (User Defined) Minute(s)
schedule.every(30).minutes.do(main)
print('~~~~~~~~~~~~~~~~~~~~~~~')
print()
print('~~~~~~~~~~~~~~~~~~~~~~~')

while True:
    schedule.run_pending()
    time.sleep(1)
import os
import shutil
import time
from ast import Assert
from lib2to3.pgen2 import driver
from multiprocessing.connection import wait

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from UploadpdfToGoogleDrive import UploadPdftoGdrive


class Downloadpdffromwebsite:
    def __init__(self):
        self.chrome_path = "C:\\Users\\user\\AppData\\Local\\Temp\\Rar$EX00.687\\chromedriver"#set your own webdriver.exe file path
        #options setup:
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("start-maximized");
        self.chrome_options.add_argument("disable-infobars")
        self.chrome_options.add_argument("--disable-extensions")
        prefs = {"download.default_directory" : "C:\\Users\\user\\Desktop\\iman\\DataImbalanced\\NoorsBooksScraping\\Download"}
        self.chrome_options.add_experimental_option("prefs",prefs)
        #initialize webdriver state
        self.driver = webdriver.Chrome(self.chrome_path,chrome_options=self.chrome_options)


        # method to get the downloaded file name
    def get_and_rename_downLoaded_file_name(self,new_name_file,download_path,waitTime=20):
        
        file_not_exist=True
        # function to wait for all chrome downloads to finish
        def chrome_downloads(drv):
            
            if not "chrome://downloads" in drv.current_url: # if 'chrome downloads' is not current tab
                drv.execute_script("window.open('');") # open a new tab
                drv.switch_to.window(self.driver.window_handles[1]) # switch to the new tab
                drv.get("chrome://downloads/") # navigate to chrome downloads
            return drv.execute_script("""
                return document.querySelector('downloads-manager')
                .shadowRoot.querySelector('#downloadsList')
                .items.filter(e => e.state === 'COMPLETE')
                .map(e => e.filePath || e.file_path || e.fileUrl || e.file_url);
                """)
        # wait for all the downloads to be completed
        while file_not_exist==True:
            dld_file_paths = WebDriverWait(self.driver, 120, 1).until(chrome_downloads) # returns list of downloaded file paths
            # Close the current tab (chrome downloads)
            if "chrome://downloads" in self.driver.current_url:
                self.driver.close()
            # Switch back to original tab
            self.driver.switch_to.window(self.driver.window_handles[0]) 
            # get latest downloaded file name and path
            dlFilename = dld_file_paths[0] # latest downloaded file from the list
            # wait till downloaded file appears in download directory
            time_to_wait = waitTime # adjust timeout as per your needs
            time_counter = 0
            while not os.path.isfile(dlFilename):
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:
                    break
            # rename the downloaded file
            try:
                os.rename(os.path.join(download_path, dlFilename), os.path.join(download_path, new_name_file))
                file_not_exist=False
                break
            except:
                pass
        return

    #function to login to the website account
    def login_to_website(self,login_url='https://www.website.com/login',user_name='username@gmail.com',pass_word='*****'):#set your own acount credintials
        #login to website account manually:
        self.driver.get(login_url)
        try:
            WebDriverWait(self.driver, 60).until(
                   EC.element_located_selection_state_to_be((By.CLASS_NAME, "submit-login"),is_selected=True))
        except:  
            print('you are not logged in please try again later.')
        #login to website account auatomatically:

        #user_name_box=self.driver.find_element(By.NAME,"email"
        #user_name_box.clear()
        #user_name_box.send_keys(user_name)
        
        #pass_word_box=self.driver.find_element(By.NAME,'password')
        #pass_word_box.clear()
        #pass_word_box.send_keys(pass_word)

        #login_btn=self.driver.find_element(By.CLASS_NAME,'submit-login')
        #login_btn.click()

    def all_pdf_download(self,base_url,download_path,file_name,file_path):
        
        self.driver.minimize_window()
        self.driver.get(base_url)
        #remove adds from website page.
        all_iframes = self.driver.find_elements(By.CLASS_NAME,"adsbygoogle")
        print(len(all_iframes))
        if len(all_iframes) > 0:
            print("Ad Found\n")
            self.driver.execute_script("""
                var elems = document.getElementsByClassName("adsbygoogle"); 
                for(var i = 0, max = elems.length; i < max; i++)
                     {
                         elems[i].hidden=true;
                         elems[i].remove=true;

                     }
                                  """)
        #click download button
        button = self.driver.find_element(By.CLASS_NAME,"download_button")#set the class name up on your website page source info
        button.click()
        self.driver.maximize_window()
        try:
            button = WebDriverWait(self.driver, 300).until(
               EC.element_to_be_clickable((By.CLASS_NAME, "internal_download_link")))#set the class name up on your website page source info

            button.click()
        except:

            print("{base_url} Not downloaded")
            return {base_url : 0}
             
        #it is important to wait for the download process to be stablished successfully
        time.sleep(5)
        #function to wait for the file to be downloaded, locate the file 
        # and then rename the file with the expected file name(id)
        self.get_and_rename_downLoaded_file_name(60,file_name,file_path)
        return {base_url : 1} 
    #function to close the connection.
    def close_connection(self):
        self.driver.close()
    
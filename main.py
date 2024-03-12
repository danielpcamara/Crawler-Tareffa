import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep


class CompanyPage:
    def __init__(self, url, un, cod_erp, razaosocial):
        self._URL = str(url)
        self._UN = []
        self._cod_erp = str(cod_erp)
        self._nome = str(razaosocial)
        if not pd.isna(un):
            temp_un_int = []
            temp_un = str(un).split(";")
            for un in temp_un:
                temp_un_int.append(int(un))

            self._UN = temp_un_int

    def __str__(self):
        return 'URL: ' + str(self._URL)
    
    @property
    def url(self):
        return self._URL

    @property
    def UN(self):
        return self._UN

    def update_caracteristics(self, browser):
        browser.get(self.url)
        sleep(0.5)

        # Select the characteristic Tab
        xpath_caracteristica = '//div[@class="mat-tab-label-content" and contains(text(),"Características")]'
        browser.find_element(By.XPATH, xpath_caracteristica).click()

        # Select the UN (04) characteristic group
        xpath_caracteristica04 = '//a[contains(text(),"04. Unidade de Negócio")]'
        WebDriverWait(browser, 90).until(EC.presence_of_element_located((By.XPATH, xpath_caracteristica04)))
        browser.find_element(By.XPATH, xpath_caracteristica04).click()

        # Wait to load
        all_un = '//*[@class="container d-flex flex-wrap"]/*/div/app-checkbox/div/div/input'
        WebDriverWait(browser, 90).until(EC.presence_of_element_located((By.XPATH, all_un)))

        # Check yes and Unchek no
        elements_un = browser.find_elements(By.XPATH, all_un)
        i = 1
        for element in elements_un:

            if i in self.UN and not element.is_selected():
                element.find_element(By.XPATH, "./..").click()   # Check
            if not(i in self.UN) and element.is_selected():
                element.find_element(By.XPATH, "./..").click()   # UnCheck
            i += 1


class TareffaSite:

    def __init__(self, browser):
        self.browser = browser

    @property
    def main_url(self):
        return "https://web.tareffa.com.br"
    
    def login(self):
        with open('config.json') as file:
            credentials = json.load(file)

        self.browser.get(self.main_url)
        self.browser.find_element(By.ID, 'username').send_keys(credentials['user'])
        self.browser.find_element(By.ID, 'password').send_keys(credentials['key'])
        self.browser.find_element(By.ID, 'btn-login').click()

        self.browser.find_element(By.CLASS_NAME, 'oauthuser').find_element(By.XPATH, '//button').click()

        WebDriverWait(self.browser, 90).until(EC.presence_of_element_located((By.XPATH, '//img[@alt="User"]')))
    
    def xpath_wait_click(self, tx_xpath):
        WebDriverWait(self.browser, 90).until(EC.presence_of_element_located((By.XPATH, tx_xpath)))
        self.browser.find_element(By.XPATH, tx_xpath).click()    

    def set_size_attibutes_gourp(self, id=19302945):
        self.browser.get(f"https://web.tareffa.com.br/empresas/{id}")

        # Select "Características" Menu
        self.xpath_wait_click('//div[@role="tab"]/div[contains(text(), "Características")]')

        #Load 50 at a time
        self.xpath_wait_click('//div[contains(text(), "Itens por página")]/../mat-form-field')
        self.xpath_wait_click('//span[contains(text(), " 50 ")]')

    def update_client_attributes(self, id, list_of_changes):
        self.browser.get(f"https://web.tareffa.com.br/empresas/{id}")

        # Select "Características" Menu
        self.xpath_wait_click('//div[@role="tab"]/div[contains(text(), "Características")]')


        # Check or UnCheck
        WebDriverWait(self.browser, 90).until(EC.presence_of_element_located((By.XPATH, '//mat-cell')))
                                                                             
        attribute_groups = self.browser.find_elements(By.TAG_NAME, 'mat-cell')

        for element_group, changes in zip(attribute_groups, list_of_changes):
            change_others = True # by default all items are changed, they wont only if 'M' is inform in the first space of the group
            if changes[0] == 'N/A':
                continue
            #print(element_group.find_element(By.TAG_NAME, 'a').text, changes)
            if element_group.find_element(By.TAG_NAME, 'a').text == '01. Regime Tributário':
                subpath = './../label'
            else:
                subpath = './..'
            if changes[0] == 'M':
                change_others = False

            element_group.click()
            sleep(0.5)

            all_attributes = '//*[@class="container d-flex flex-wrap"]/*/div/app-checkbox/div/div/input'
            WebDriverWait(self.browser, 90).until(EC.presence_of_element_located((By.XPATH, all_attributes)))

            elements_att = self.browser.find_elements(By.XPATH, all_attributes)
            i = 1
            had_changes = False
            for element in elements_att:

                need_to_change = (str(i) in changes and not element.is_selected()) or (not(str(i) in changes) and element.is_selected() and change_others)

                if need_to_change:
                    element.find_element(By.XPATH, subpath).click()   # Check
                    had_changes = True
                i += 1
            if had_changes:
                sleep(0.5)

    def get_company_list(file, browser):
        shtcompany = pd.read_excel(file)
        browser.get("https://web.tareffa.com.br/empresas")
        sleep(3)
        list_of_companies = []
        for index, c in shtcompany.iterrows():
            url = c['URL']
            if c['Andamento'] == "Check URL":
                url = update_url(browser, c['codigoquestor'], c['razaosocial'])
                print(url)
            if c['Andamento'] != "OK":
                company = CompanyPage(url, c['UN Correta'], c['codigoquestor'], c['razaosocial'])
                list_of_companies.append(company)
        return list_of_companies


def main():

    browser = webdriver.Chrome()

    tareffa_site = TareffaSite(browser)
    tareffa_site.login()
    
    list_of_changes = get_list_of_changes('Base Atualização.xlsx', 'Alterações')

    for row in list_of_changes.iterrows():  # loop through all rows in the Spredsheet sites
        tareffa_site.update_client_attributes(row[1]['idempresa'], row[1]['Alterações'])

    input("Press Enter to end this.")
    browser.quit()

def get_list_of_changes(path, sht_name, id_col_name='idempresa', changes_col_name='Alterações'):
    def convert_to_list(tx_modify):
        temp_list = tx_modify.split("|")
        list_of_changes = list(x.split(";") for x in temp_list)
        return list_of_changes


    sht_changes = pd.read_excel(path, sht_name)
    sht_changes = sht_changes[[id_col_name, changes_col_name]]
    sht_changes[changes_col_name] = sht_changes[changes_col_name].apply(convert_to_list)
    return sht_changes


def update_url(browser, cod_erp, company_name):
    cod_erp = str(cod_erp)
    company_name = str(company_name)

    browser.find_element(By.XPATH, '//*[@id="mat-input-0"]').clear()
    browser.find_element(By.XPATH, '//*[@id="mat-input-0"]').send_keys(cod_erp)
    browser.find_element(By.XPATH, '//*[@id="mat-input-1"]').clear()
    browser.find_element(By.XPATH, '//*[@id="mat-input-1"]').send_keys(company_name)

    search = browser.find_elements(By.XPATH, '//*[@class="svg-inline--fa fa-search fa-w-16 text-dark cursor-pointer"]')
    search[0].click()
    search[1].click()
    sleep(3)
    new_url = browser.find_element(By.XPATH,
                                    '//*[@class="mat-row cdk-row ng-star-inserted"]/mat-cell[2]/a').get_attribute(
        'href')
    return new_url


if __name__ == '__main__':
    main()

# About

Tareffas is a task maneger web app. "https://web.tareffa.com.br/".

This site is able to bulk insert Companys from csv files. However, the _"Características"_ (attributes) of this companys can't be define from the CSV file.

To overcome this limitarion, this crawler uses selenium to update this fiels base on a Excel workbook.

# Workbook layout

The workbook must have a worksheet with **at least** 2 columns:
* _idempresa_:  the company ID present in the sites URL
* _Alterações_: A structure list that informs for every _"Grupo de Características"_ (attribute group), wich attribute must be enable.
    * The groups **must** be sorted with the same site's order
    * Every group must be separated by pipe (```|```)
    * If the group should not be changed, inform "N/A"
    * Otherwise informe the relative position of evrey attribute that must be enable, seperated by semicolon (```;```).

A sample file is available in this repo with one Exemple.

# Requirements
```
pip install pandas
pip install openpyxl
pip install selenium
```
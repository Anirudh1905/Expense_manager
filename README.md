# Expense Manager
Categorization of expense from account statement\
\
Firstly download the account statement from bank website and store it as .csv\
**Requirement :** pip install fuzzywuzzy 
  
## Arguments
**--input :** input csv path\
**--data :** data dict file which contains mapping of categories\
**--month :** account statement month name\
**--output_img :** output image file path\
**--output_csv :** output csv path. 

## How to run?
python expense_manager.py --input "input filepath" --data "data.json" --month "month-name" --output_img "output dir path/" --output_csv "output dir path/"

## Debit Pie Chart
![Debit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/January%20Debit.png)

## Credit Pie Chart
![Credit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/January%20Credit.png)

## Credit vs Debit Pie Chart
![Credit vs Debit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/January%20Credit%20vs%20Debit.png)

# Expense Manager
Categorization of expense from account statement\
\
Firstly download the account statement from bank website and store it as .csv\
**Requirement :** pip install fuzzywuzzy 
  
## Arguments
**--input :** input csv path\
**--data :** data dict file which contains mapping of categories\
**--month :** account statement month name\
**--output_path :** output dir path\
**--sub_category :** show debit sub category plot (optional by default false)

## How to run?
python expense_manager.py --input "data/input filepath" --data "data/data.json" --month "month-name" --output_path "output dir path" --sub_category True

## Credit Pie Chart
![Credit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/outputs/January%20Credit.png)

## Debit Pie Chart
![Debit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/outputs/January%20Debit.png)

## Sub Category Debit Pie Chart
![Sub Category Debit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/outputs/January%20Sub%20Category%20Debit.png)

## Credit vs Debit Pie Chart
![Credit vs Debit Pie Chart](https://github.com/Anirudh1905/Expense_manager/blob/main/outputs/January%20Credit%20vs%20Debit.png)

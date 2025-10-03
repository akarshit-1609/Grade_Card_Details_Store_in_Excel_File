# IGNOU Grade Card Details Store in MySql Database and also export in excel file


## Requirements

To run this program, you will need:

* **Python 3.6 or higher:** Ensure you have a compatible version of Python installed.
* **MySQL Server:** You need to have a MySQL server installed and running on your local machine and also MySQL <i>bin</i> directory should be added in your system's PATH environment variable. The program will connect to this instance.
* **Required Python Libraries:** The following libraries are necessary and will be installed using pip.

## Installation

* **Clone the repository:**
    ```bash
    git clone https://github.com/akarshit-1609/Grade_Card_Details_Store_in_MySql_Database.git
    ```
    **Or download this repository.**

* **Install Required Python Libraries:**

   Navigate to the program's directory in your terminal and install the necessary libraries using pip:

   ```bash
   cd program_directory
   pip install -r requirements.txt

## Setup Instruction

* **Change Variables in Source Code Before Run:**
    
    #### In grade_card.py
    * For mysql configuration:
    ```code
    rootuser = mysql.connector.connect(
        host="Your hostname",
        user="Your Username",
        password="Your Password",
        port="Your port "
    )

    mysql_exe = "mysql"     # Path of mysql.exe
    mysql_login_file = "--defaults-file=mylogin.cnf"    # Path of mylogin.cnf
    ```
    #### In mylogin.cnf
    * Modify values if not match your mysql configuration.
    #### After Configuration
    * After this change navigate to the program's directory in your terminal and run program like this:
    ```bash
    cd program_directory
    python grade_card.py
    ```
    If succesfully run program without an error than you fetch your marks and automatically store in mysql database and you can export marks in Excel file.

## How to use

* After run this program a gui window will be appear.

* Enter Enrolnment number in first input field, replace to your programme code in second input field and also replace to your programmes type in third input field then click fetch button.

* After you got done message then click on dropdown list and select your name.

* After select your name, click on show button and your marks will be show in terminal.

* Also you can export your marks in excel file which is save on desktop folder in your computer.

* **To see your all data which is store in mysql:**

    In the mysql CLI:
    ```bash
    mysql> use grade_cards;
    mysql> show tables;
    ```

**Portfolio Calculator**
**Overview**
The Portfolio Calculator is a Python-based application that allows users to analyze their investment portfolios by calculating the current value and gain/loss based on transaction data provided in a JSON file. The application fetches the latest Net Asset Values (NAV) of mutual funds using the mstarpy library and presents a detailed report through a graphical user interface (GUI) built with Tkinter.

**Features**
Load transaction data from a JSON file.
Calculate the total portfolio value and gain/loss for each fund.
Fetch NAVs for various funds in parallel to enhance performance.
Display results in a user-friendly format.

**Requirements**
Python 3.6 or higher
Required libraries (see requirements.txt for details)
Installation

Clone the repository:

bash
git clone https://github.com/priyaelangovan723/Backend_Assignment_1.git
cd Backend_Assignment_1

Install the required libraries:

You can install the required libraries using pip. Create a virtual environment and run:
bash
pip install -r requirements.txt
Run the application:

Open a terminal and execute the following command:
bash
python portfolio_calculator.py
**Usage**
Upon launching the application, click the **"Load Transaction File" button to select your JSON file** containing the transaction data.
The application will process the data and display the portfolio details and summary in the text area.
Review the calculated total portfolio value and gain/loss for each fund.

**JSON Structure**
The application expects the transaction data to follow a specific JSON structure. Here's an example of the expected structure:

![image](https://github.com/user-attachments/assets/abf8c043-7f02-4f82-b5a5-575deac0f989)

**Caching**
The application employs a** caching mechanism to store NAV data locally**, which** minimizes the number of API calls and speeds up subsequent requests** for the same ISIN.

**Contributing**
If you would like to contribute to this project, feel free to open an issue or submit a pull request. Your contributions are welcome!

**License**
This project is licensed under the MIT License. See the LICENSE file for more details.

**Acknowledgments**
mstarpy for fetching mutual fund data.
Tkinter for building the GUI.

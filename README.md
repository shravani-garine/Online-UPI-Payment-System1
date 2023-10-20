README

# Introduction

This is an online UPI payment system built using Python, SQL Server, Flask, Bootstrap, JavaScript, HTML, and CSS. It has separate login and register pages, and users can send money, manage their profile, link their bank account, view their transaction history, receive notifications, and see their account balance on the dashboard.

# Dependencies

The following Python libraries are required to run this project:

- bcrypt==4.0.1
- blinker==1.6.3
- click==8.1.7
- colorama==0.4.6
- Flask==3.0.0
- Flask-Bcrypt==1.0.1
- itsdangerous==2.1.2
- Jinja2==3.1.2
- MarkupSafe==2.1.3
- pyodbc==5.0.0
- Werkzeug==3.0.0
- Installation

To install the dependencies, run the following command in a terminal:

```pip install -r requirements.txt```

Once the dependencies are installed, you can start the project by running the following command:

```flask run```

This will start the Flask development server on port 5000. You can then access the application in your web browser at http://localhost:5000/.

# Features

## Login and registration: 
Users can create an account and log in to the system.
## Money transfer: 
Users can send money to other users by entering the recipient's UPI ID and the amount to transfer.
## Profile management: 
Users can manage their profile information, including their name, email address, and UPI ID.
## Bank account linking: 
Users can link their bank accounts to their UPI account.
## Transaction history: 
Users can view their transaction history, including date, time, sender/receiver information, and transaction status.
## Notifications: 
Users receive email or SMS notifications for successful transactions and account activities.
## Dashboard: 
Users can view their account balance and recent transactions on the dashboard.


# Logging and exception handling

The project maintains a log file to record all system events. Exception handling is also implemented to handle any errors that may occur.

# Conclusion

This is a secure and convenient way to make and receive payments online. It is easy to use and accessible to everyone, regardless of their technical expertise.
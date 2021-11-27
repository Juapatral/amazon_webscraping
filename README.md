# **AMAZON WEBSCRAPING**

This is a personal project I started with my frieds to keep track of products of [Amazon](https://www.amazon.com) that we wanted and get an alert if it suddenly received a massive price drop for Black Friday / Cyber Monday / Holidays.

**NOTE:** This repo is ***extremely*** difficult to maintain due to constant CSS changes on amazon's website. We work on this project on our free time, thus we hope you understand if you arrive here and it has not been updated. Thank you and get coding! 

**NOTE2:** This repo is also a way to practice coding and increase our experience, therefore errors may be common. If you have any suggestions or improvements, set a pull requests and we will check it ASAP.

## **Preparations**

From a terminal 

1. Clone this project.

    ```git clone https://github.com/Juapatral/amazon_webscraping``` 

2. Cd into it. 
    
    ```cd amazon_webscraping```

3. (Optional) Add a Virtual Environment.

    ```python3 -m venv your-virtual-env```

4. (Optional) Activate the Virtual Environment with either

    ```your-virtual-env/Scripts/activate```

    ```source .venv/bin/activate```

5. Install Requirements.
    
    ```pip3 install -r requirements.txt```

## **File preparations**

There are three files you must create that are located in the `files` folder:

* ### Wishlist, in `wishlist` folder.
    This file is going to be filled with the products you wish to scrap information. At least an url must be provided. Check `sample_shopping_list.csv` for a guide.
    
* ### Users, in `users` folder.
    This file is going to be filled with the users and their contact information to send messages. Check `sample_users_info.csv` for a guide.

* ### Results, in `results` folder.
    This file is going to be filled with the results of the scraped information. It is not necessary to have information before running, but it is *highly suggested* to create a new csv file with the exact same titles, to conserve the original structure. Check `sample_shopping_list_searched.csv` for a guide.    

## **Execution**
To execute call bat file with paths to your wishlist, users, and results files.

```cmd
scripts\execute.bat path\to\your_shopping_list.csv path\to\your_users_info.csv path\to\your_shopping_list_searched.csv
```

After each execution a log file will be created inside the `logs` folder.

## **Additional information**
* [Common user agent list for headers and cookies.](http://www.networkinghowtos.com/howto/common-user-agent-list/)
* [Logging](https://realpython.com/python-logging/)

## **Backlog (not ordered)**
* Non-specific search.
* Testing.
* Refactoring and optimization.
* Search API.
* Precommit configuration.
* Deploy in Linux and Windows.
* Docker App.
* Web of history prices.
* Database API.

## **Credits**
* Github: [Juapatral](https://www.github.com/Juapatral)
* Created: November, 2021
* Medellín, Colombia


In this assignment, you will normalize a dataframe of scraped data from **First Normal Form (1NF)** to **Third Normal Form (3NF)** and save the resulting tables into a **SQLite database**. You will submit your completed assignment by saving the database file in the specified directory and updating your Git repository.  

1. **Given Data**: You will start with all of the html files of your classmates' introductions. I suggest starting by gathering all tabular data into a 1NF dataframe with columns *first_name* (str), *last_name* (str), *category* (str), *favorite* (str).
2. **Normalization Task**: You will transform this data into two tables, each in **Third Normal Form (3NF)**.
3. **Write to SQLite**: You will store these two tables in a SQLite database file.
4. **Submission**: Save the SQLite file to *data/assignment_4/altered/class_info.sqlite3* and update your Git repository.

Your final sqlite database should have the following table:column structure:
*students*: *name_id* (int pk), *first_name* (str), *last_name* (str)
*favorites*: *name_id* (fk), *category* (str), *favorite* (str)
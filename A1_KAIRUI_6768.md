Author:  YAO KAIRUI
ID: 20406768


Functional Requirements     Function Name                       Implementation Status         What is Missing

R1                                       add_book_to_catalog               Complete                             All R1 requirements fully implemented with proper input validation, duplicate checking, and database operations.


R2                                                                                          Missing                                Missing corresponding function in Library_service.py


R3                                       borrow_book_by_patron          Complete                             All R3 requirements fully implemented with patron ID validation, book availability check, borrowing limit enforcement, and proper database updates.


R4                                       return_book_by_patron            Missing                                No business logic has been implemented, only "return False".  Needs patron verification, return date recording, availability update, and late fee calculation integration


R5                                       calculate_late_fee_for_book      Missing                                Thie is a empty function. Needs actual late fee calculation logic.


R6                                       search_books_in_catalog          Missing                                 No business logic has been implemented, only returns empty list. Needs to search functionality with partial matching for title/author.


R7                                       get_patron_status_report         Missing                                  No business logic has been implemented, only returns empty ldictionary. Needs to implement currently borrowed books with due dates, total late fees owed, number of books borrowed, and borrowing history.



Summary:​​
​​Fully Implemented:​​ R1 (add_book_to_catalog) and R3 (borrow_book_by_patron)
​​Completely Missing:​​ R2, R4 (return_book_by_patron), R5 (calculate_late_fee_for_book), R6 (search_books_in_catalog), R7 (get_patron_status_report)
​​No Partial Implementations:​​ All missing functions have only placeholder/stub implementations without any actual business logic.
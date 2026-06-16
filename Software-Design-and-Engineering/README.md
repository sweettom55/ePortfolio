# Software Design and Engineering Enhancement

## Artifact: CS 360 Mobile Inventory Application

This artifact is an Android mobile inventory application originally developed in CS 360 Mobile Architecture and Programming using Kotlin, Android Studio, and SQLite. The application allows a user to create an account, log in, and manage inventory items through add, edit, and delete functionality.

## Enhancement Overview

For the CS 499 Software Design and Engineering enhancement, I improved the application by addressing security, data integrity, navigation, and usability concerns identified during testing and code review.

The completed enhancements include:

* Added salted PBKDF2 password hashing so user passwords are no longer stored as readable text.
* Added automatic conversion of previously stored readable passwords after a successful login.
* Prevented duplicate inventory entries when item names differ only by capitalization.
* Added validation that rejects negative inventory quantities.
* Improved add and edit dialog behavior so users can correct invalid input without reopening the dialog.
* Added delete confirmation before inventory records are permanently removed.
* Improved the inventory layout so column headings remain visible after inventory data refreshes.
* Added a Log Out option with confirmation and activity history clearing to prevent returning to the inventory screen after logout.

## Skills Demonstrated

This enhancement demonstrates skills in Kotlin development, Android user interface design, SQLite database integration, input validation, secure credential handling, application navigation, iterative testing, and software improvement based on identified design weaknesses.

## Course Outcome Alignment

This artifact demonstrates progress toward implementing computing solutions that deliver value through improved reliability and usability. It also demonstrates a security mindset by addressing the risk of readable password storage and improving session control through the addition of a logout feature.

## Repository Contents

* [Original Inventory App](./CS%20499%20Inventory%20App%20Original.zip)
* [Enhanced Inventory App](./CS%20499%20Inventory%20App%20Enhanced.zip)
* [Software Design and Engineering Narrative](./Software-Design-and-Engineering-Narrative.docx)

## Supporting Screenshots

* [Inventory Screen](./Inventory-Screen.png)
* [Duplicate Item Validation](./Item-Already-Exists.png)
* [Log Out Feature](./Log-Out.png)
* [Password Security Enhancement](./Password.png)
* [Negative Quantity Validation](./Quantity-Cant-Be-Negative.png)

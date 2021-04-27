# Meetings notes

## Meeting 1.
* **DATE:** 12.2.2021
* **ASSISTANTS:** Mika Oja

### Minutes
*Things that needed to be changed:*

*Overview shouldn't include reference to the implementation of the client and in the API uses client refers to the machine clients instead of the end users. Related work is a little bit confusing and needs to be thought again.*


### Action points
*Fix the parts discussed in "Minutes":*

* *Write overview partially again.*
* *Write API uses again.*
* *Make Related work more understandable and extend it.*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 2.
* **DATE:** 26.2.2021
* **ASSISTANTS:** Mika Oja

### Minutes
*Discussed the tables and which parts need correcting. The actual implementation is close to what was used in Lovelace materials, and it is quite simple and seems to be correctly implemented.*

### Action points
* *Foreign key reference should be in the referencing end of the bankaccount table.*
* *Datetime is a specification, change that to the table.*
* *Remember to test if user goes to null if some relationship -instance is deleted.*

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 3.
* **DATE:** 18.3.2021
* **ASSISTANTS:** Mika Oja

### Minutes
*The "Uniform Interface" -table needs updating, as it is not quite the same as in the implementation. In the Apiary there are minor fixes to be made and also we need to consider what parts should be made public and what should not (for example the user password). Schema was also missing in some parts. REST conformance -part is too short, we should extend it.*

### Action points
* *Update "Unifor Interface" -table according to the implementation.*
* *In the Apiary, the transaction schema user objects should be replaced with strigs.*
* *User collection shouldn't include passwords or other private information.*
* *Bankaccount edit needs a schema.*
* *Link relation's collection names should be corrected: bumeta:edit -> edit.*
* *Extend REST conformance.*

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 4.
* **DATE:** 13.4.2021
* **ASSISTANTS:** Mika Oja

### Minutes
*Since the code is partially made by someone else, it should be mentioned in the beginning of the code. In the implementation, it would be useful to be able to get from one collection to another. For example, from Users to Transactions. We were also discussing minor fixes that the client code needs. We should also consider the test coverage, if we are missing or forgetting something.*

### Action points
* *Methods are missing doc strings, add them.*
* *Test coverage needs to be increased.*
* *Add comment to the beginning of the code, where the code is borrowed.*
* *In the transaction tests we haven't defined dbreceiver, that should be done.*
* *Implement movement between collections.*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*


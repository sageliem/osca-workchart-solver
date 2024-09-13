# OSCA WORKCHART SOLVER
Linear solver for simple scheduling.
## Instructions
Format availability responses as CSV. You can export CSV directly from Google Sheets, Google Form responses, or Excel files. You will need to edit the column indices in workchart.py to match your data (or vice versa).

The solver uses PuLP, a linear optimization library. You can install PuLP using ```pip```:
 
```
python -m pip install pulp
```
To run the script:
```
python workchart.py <PATH_TO_FILE>
```
## Planned features
- Full integration with google forms
- Options for different workchart structures

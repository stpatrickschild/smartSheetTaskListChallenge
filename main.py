from flask import Flask, request
import json
import smartsheet
import uuid

app = Flask(__name__)

smart = smartsheet.Smartsheet()             # Create a Smartsheet client 
response = smart.Sheets.list_sheets()       # Call the list_sheets() function and store the response object
sheetId = response.data[0].id               # Get the ID of the first sheet in the response
sheet = smart.Sheets.get_sheet(sheetId)     # Load the sheet by using its ID

print(f"The sheet {sheet.name} has {sheet.total_row_count} rows")   # Print information about the sheet



@app.route('/')
def index():
    return 'Hello from Flask!'


@app.route('/tasks', methods=["GET"])
def list_tasks():
  result = []
  for row in sheet.rows:
    result.append({
      "rowId":row.id,
      "created_at":str(row.created_at),
      "modified_at": str(row.modified_at),
      "row": row.to_dict()})

  return json.dumps(result)

@app.route('/task', methods=["POST"])
def create_task():
  print(request.form)
  response = smart.Sheets.get_columns(
    sheetId,
    include_all=True)
  columns = response.data

  new_task = smartsheet.models.Row()    # creating a row

  for col in columns:                   # iterating throught the row and getting the value
    if not col.primary:
      new_task.cells.append({             # of each col, assuming that the name matches
        'column_id':col.id,
        'value': request.form.get(col.title)       #request.form is being getting from reqest
                                                   # body
      })
    else:
      new_task.cells.append({             # of each col, assuming that the name matches
        'column_id':col.id,
        'value': str(uuid.uuid4())
      })

  response = smart.Sheets.add_rows(
    sheetId,
    [new_task])

  result = []
  for row in response.result:
    result.append({
      "rowId":row.id,
      "created_at":str(row.created_at),
      "modified_at": str(row.modified_at),
      "row": row.to_dict()})
  return json.dumps(result)
    
  
@app.route('/task', methods=["PATCH"])
def update_task():
  # get task using task id from request body
  task =  smartsheet.models.Row()
  task.id = int(request.form.get("rowId"))
  
  # update task columns using values from request body
  response = smart.Sheets.get_columns(
    sheetId,
    include_all=True)
  columns = response.data

  
  for col in columns:                 
    if not col.primary and col.title in request.form:
      new_cell = smartsheet.models.Cell()
      new_cell.column_id = col.id
      new_cell.value = request.form.get(col.title)
      task.cells.append(new_cell)
    
  # send request to update row
  task.created_at = None
  task.modified_at = None
  response = smart.Sheets.update_rows(
    sheetId,      # sheet_id
    [task])

  result = []
  for row in response.result:
    result.append({
      "rowId":row.id,
      "created_at":str(row.created_at),
      "modified_at": str(row.modified_at),
      "row": row.to_dict()})
  return json.dumps(result)
  
@app.route('/task', methods=["DELETE"])
def delete_task():
  smart.Sheets.delete_rows(
    sheetId,                       # sheet_id
    [request.form.get("rowId")])     # row_ids
  return "ok", 200


app.run(host='0.0.0.0', port=81)





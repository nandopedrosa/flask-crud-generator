import os
import config


def __get_route_signature(name: str, model: str, login_required: bool, methods: str, has_param=False, param="id") -> str:

    if(has_param):
        sig = f"@{model}_bp.route('<int:{param}>/{name}', methods=({methods}))"
    else:
        sig = f"@{model}_bp.route('/{name}', methods=({methods}))"

    if login_required:
        sig += "\n@login_required\n"

    if(has_param):
        sig += f"def {name}({param}):\n"
    else:
        sig += f"def {name}():\n"
    return sig


def generate_view(model: str, login_required: bool, target_directory: str):
    f = open(os.path.join(target_directory, "views.py"), "w")

    # imports
    f.write("from flask import Blueprint, render_template, request, flash, redirect, url_for\n")
    if login_required:
        f.write("from app.auth.views import login_required\n")
    f.write("from app.util.validation import Validation\n")
    f.write(f"from app.{model} import service\n\n")

    # blueprint
    f.write(f"{model}_bp = Blueprint('{model}', __name__,template_folder='templates',static_folder='../static', url_prefix='/{model}')\n\n")

    # routes

    # Create
    f.write(__get_route_signature("create", model, True, "'GET','POST'"))
    f.write(
        f"\tif request.method == 'POST':\n\t\tv = service.save(request)\n\t\tflash(v.message, category=v.status)\n\t\tif v.status == Validation.STATUS_OK:\n\t\t\treturn redirect(url_for('{model}.list'))")
    f.write("\n\n")
    f.write(f"\treturn render_template('{model}/edit.html', {model}=None)")
    f.write("\n\n")

    # List
    f.write(__get_route_signature("list", model, True, "'GET',"))
    f.write(
        f"\tmodel_collection = service.list()\n\treturn render_template('{model}/list.html', model_collection=model_collection)")
    f.write("\n\n")

    # Delete
    f.write(__get_route_signature(
        "delete", model, True, "'POST',", has_param=True))
    f.write("\tservice.delete(id)\n\tflash('Registro excluído com sucesso.', category=Validation.STATUS_OK)\n\treturn ''")
    f.write("\n\n")

    # Update
    f.write(__get_route_signature("update", model,
            True, "'GET','POST'", has_param=True))
    f.write(f"\t{model} = service.find_by_id(id)\n")
    f.write(
        f"\tif request.method == 'POST':\n\t\tv = service.save(request)\n\t\tflash(v.message, category=v.status)\n\t\tif v.status == Validation.STATUS_OK:\n\t\t\treturn redirect(url_for('{model}.update', id=id))")
    f.write("\n\n")
    f.write(f"\treturn render_template('{model}/edit.html', {model}={model})")
    f.write("\n\n")


def generate_service(model: str, model_class_name: str, target_directory: str):
    f = open(os.path.join(target_directory, "service.py"), "w")

    # imports
    f.write("from flask import request\n")
    f.write("from typing import List\n")
    f.write("from app.util.validation import Validation\n")
    f.write(f"from app.{model}.model import {model_class_name}\n")
    f.write(f"from app.{model} import dao\n\n")

    # functions

    # Validate
    f.write(
        f"def __validate_{model}() -> Validation: #fill with validation parameters\n")
    f.write("""\tif(not Validation.filled([])): #fill with mandatory parameters
        \treturn Validation(message="Por favor, preencha todos os campos obrigatórios.",
                          status=Validation.STATUS_ERROR)""")
    f.write("\n\n")
    f.write("\t#fill with other validations")
    f.write("\n\n")
    f.write("\treturn Validation(status=Validation.STATUS_OK)\n\n")

    # Save
    f.write(
        f"def save(r: request) -> Validation:\n\tid = r.form['id'] if 'id' in r.form else None\n\t#fill with other request parameters\n\n\tv = __validate_{model}() #fill with validation parameters\n\n")
    f.write(f"""\tif v.status == Validation.STATUS_OK:\n\t\t{model} = {model_class_name}(dict(r.form))
        if id:
            dao.update({model})
            v.message = "{model_class_name} atualizado com sucesso."
        else:  
            id = dao.insert({model})
            v.message = "{model_class_name} criado com sucesso."

        v.payload = id\n\n""")
    f.write("\treturn v\n\n")

    # List
    f.write(
        f"""def list() -> List[{model_class_name}]:\n\treturn dao.fetch_all()\n\n""")

    # Delete
    f.write("""def delete(id: int):\n\tdao.delete(id)\n\n""")

    # Find
    f.write(
        f"""def find_by_id(id: int) -> {model_class_name}:\n\treturn dao.find_by_id(id)\n\n""")


def generate_dao(model: str, model_class_name: str, target_directory: str):
    f = open(os.path.join(target_directory, "dao.py"), "w")

    # imports
    f.write(f"""from typing import List
from app.{model}.model import Tag
from app.db import get_db
from flask import g
from app.util.db_converter import build_sql, lastrowid""")
    f.write("\n\n")

    # Insert
    f.write(f"def insert({model}: {model_class_name}) -> int:\n")
    f.write(f"\tdb = get_db()\n\tcur = db.cursor()\n")
    f.write(
        f"\tsql = build_sql('INSERT INTO {model} () VALUES ()') #fill with paramater$\n")
    f.write("\tcur.execute(sql,()) #fill with parameters\n")
    f.write("\tdb.commit()\n\treturn lastrowid(cur)")
    f.write("\n\n")

    # Fetch all
    f.write(f"def fetch_all() -> List[{model_class_name}]:\n")
    f.write("\treturn_list = []\n\tdb = get_db()\n\tcur = db.cursor()\n")
    f.write(
        f"\tsql = build_sql('SELECT * FROM {model} where ... = $ order by ...') # fill with parameter$\n")
    f.write(
        "\tcur.execute(sql, ()) #fill with parameters\n\tresult = cur.fetchall()\n\n")
    f.write(
        f"\tfor row in result:\n\t\t{model} = {model_class_name}(dict(row))\n\t\treturn_list.append({model})\n\n")
    f.write("\treturn return_list")
    f.write("\n\n")

    # Delete
    f.write("def delete(id: int):\n")
    f.write("\tdb = get_db()\n\tcur = db.cursor()\n")
    f.write(f"\tsql = build_sql('DELETE FROM {model} where id = $')\n")
    f.write("\tcur.execute(sql,(id,))\n")
    f.write("\tdb.commit()")
    f.write("\n\n")

    # Find by id
    f.write(f"def find_by_id(id: int) -> {model_class_name}:\n")
    f.write("\tdb = get_db()\n\tcur = db.cursor()\n")
    f.write(f"\tsql = build_sql('SELECT * FROM {model} WHERE id = $')\n")
    f.write("\tcur.execute(sql,(id,))\n")
    f.write("\tresult = cur.fetchone()\n")
    f.write(f"\t{model} = {model_class_name}(dict(result))\n")
    f.write(f"\treturn {model}")
    f.write("\n\n")

    # Update
    f.write(f"def update({model}: {model_class_name}):\n")
    f.write("\tdb = get_db()\n\tcur = db.cursor()\n")
    f.write(f"\tsql = build_sql('UPDATE tag SET ... WHERE ...') #fill with parameters\n")
    f.write("\tcur.execute(sql,()) #fill with parameters\n")
    f.write("\tdb.commit()")


def generate_model(model: str, model_class_name: str,  target_directory: str):
    f = open(os.path.join(target_directory, "model.py"), "w")

    f.write(f"class {model_class_name}():\n")
    f.write("\t# Constructor based on a dict\n")
    f.write("\tdef __init__(self, *initial_data, **kwargs):\n")
    f.write("\t\tfor dictionary in initial_data:\n")
    f.write("\t\t\tfor key in dictionary:\n")
    f.write("\t\t\t\tsetattr(self, key, dictionary[key])\n")
    f.write("\t\tfor key in kwargs:\n")
    f.write("\t\t\tsetattr(self, key, kwargs[key])")


def generate_list_html(model: str, template_directory: str):
    with open('template-list.html', 'r') as template:  # source template
        html = template.read()

    html = html.replace("#TITLE#", config.model_list_name)
    html = html.replace("#HEADER#", config.model_list_name)
    html = html.replace("#MODEL#", model)

    # Table header
    header_template = '<th scope="col">#HEADER_TITLE#</th>'
    table_header = ''
    for field in config.model_fields:
        # field title is between parenthesis
        title = field['field_label']
        table_header += header_template.replace("#HEADER_TITLE#", title)
    html = html.replace("#TABLE_HEADER#", table_header)

    # Table data
    data_template = r"<td>{{ #MODEL#.#DATA_FIELD# }}</td>"
    data_template = data_template.replace("#MODEL#", model)
    table_data = ''
    for field in config.model_fields:
        # field data is outside parenthesis
        data_field = field['field_name']
        table_data += data_template.replace("#DATA_FIELD#", data_field)
    html = html.replace("#TABLE_DATA#", table_data)

    # target generated file
    f = open(os.path.join(template_directory, "list.html"), "w")
    f.write(html)


def generate_edit_html(model: str, template_directory: str):
    with open('template-edit.html', 'r') as template:  # source template
        html = template.read()

    html = html.replace("#MODEL#", model)
    form_fields = ''

    for field in config.model_fields:
        field_type = field['field_type']
        ff = ''

        # each specific field...
        if field_type == 'textfield':
            ff = config.textfield_template.replace(
                "#FIELD_NAME#", field['field_name'])
            ff = ff.replace("#MIN_LENGTH#", config.min_length)
            ff = ff.replace("#MAX_LENGTH#", config.max_length)

        if field_type == 'textarea':
            ff = config.textarea_template.replace(
                "#FIELD_NAME#", field['field_name'])

        # applies to all fields
        ff = ff.replace("#MODEL#", model)
        if field['mandatory'] == 'y':
            ff = ff.replace("#FIELD_LABEL#", field['field_label'] + "*")
            ff = ff.replace("#REQUIRED#", "required")
        else:
            ff = ff.replace("#FIELD_LABEL#", field['field_label'])
            ff = ff.replace("#REQUIRED#", "")

        form_fields += ff + "\n\n"

    html = html.replace("#FORM_FIELDS#", form_fields)

    # target generated file
    f = open(os.path.join(template_directory, "edit.html"), "w")
    f.write(html)


def generate_all(model: str, model_class_name: str, login_required: bool):
    # make sub folders
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, "output", f"{model}")
    template_directory = os.path.join(
        current_directory, "output", f"{model}", "templates")
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    if not os.path.exists(template_directory):
        os.makedirs(template_directory)

    # generate files
    f = open(os.path.join(target_directory, "__init__.py"), "w")
    generate_view(model, login_required, target_directory)
    generate_service(model, model_class_name, target_directory)
    generate_dao(model, model_class_name, target_directory)
    generate_model(model, model_class_name, target_directory)
    generate_list_html(model, template_directory)
    generate_edit_html(model, template_directory)


def main():
    generate_all(config.model, config.model_class_name, config.login_required)


# Usage:
# model name is the plain old object name, lowercase
# login required fills the routes with a login check decorator
if __name__ == "__main__":
    main()

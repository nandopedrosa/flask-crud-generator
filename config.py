model='assunto'
login_required=True
model_class_name='Assunto'
model_list_name='Assuntos' # used in list.html

# field_name should be the same name used in the DBMS
# field_type affects how we render in the html file
# mandatory affects if we put a "*"" after the field label
model_fields=[
    {"field_name" : "name", "field_label" : "Nome", "field_type" : "textfield" , "mandatory" : "y" }    
]

#min and max length for textfield types
min_length = "3"
max_length = "128"

#---TEMPLATES---- 

#textfield
textfield_template = """<div class="mb-3">
                            <label for="#FIELD_NAME#" class="form-label">#FIELD_LABEL#</label>
                            <input placeholder="" 
                            name="#FIELD_NAME#"  value="{{ request.form['#FIELD_NAME#'] or #MODEL#.#FIELD_NAME# }}"
                            minlength="#MIN_LENGTH#" maxlength="#MAX_LENGTH#" type="text" class="form-control" id="#FIELD_NAME#" #REQUIRED#>
                        </div>"""

textarea_template = """<div class="mb-3">
                            <label for="#FIELD_NAME#" class="form-label">#FIELD_LABEL#</label>
                            <textarea name="#FIELD_NAME#" class="form-control" id="#FIELD_NAME#" rows="3" #REQUIRED#>{{request.form['#FIELD_NAME#'] or #MODEL#.#FIELD_NAME#}}</textarea>
                        </div>"""
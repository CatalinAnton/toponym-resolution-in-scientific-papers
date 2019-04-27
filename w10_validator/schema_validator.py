import json
import jsonschema
from jsonschema import ValidationError

import p1_file_management

schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Senteces",
    "description": "Analized sentences that contain toponyms",
    "type": "object",
    "properties": {
        "sentences": {
            "type": "array",
            "items": {
                "allOf": [
                    {
                        "type": "object",
                        "properties": {
                            "sentence": {"type": "string"},
                            "words": {
                                "type": "array",
                                "items": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "toponymId": {"type": "number"},
                                                "toponym": {"type": "string"},
                                                "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                                                "longitude": {"type": "number", "minimum": -180, "maximum": 180}
                                            },
                                            "required": ["toponymId", "toponym", "latitude", "longitude"]
                                        }
                                    ]
                                }
                            }
                        },
                        "required": ["sentence", "words"]
                    }
                ]
            }
        }
    },
    "required": ["sentences"]
}

files = p1_file_management.get_file_list_output_final()
dict_file_content = p1_file_management.get_dictionary_file_content(files)
for (file_path, content) in dict_file_content.items():
    print("Validating " + file_path + " ...")
json_object = json.loads(content)
try:
    jsonschema.validate(json_object, schema, format_checker=jsonschema.FormatChecker())
    print("\tJSON file is valid")
except Exception as e:
    print("\t" + str(e.message))
print("\n")

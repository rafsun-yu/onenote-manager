import json

class Model:
    """
    Representation of an entity of Microsoft Graph.
    For example, Notebook, Page, Section etc. 
    """
    
    @classmethod
    def from_json(cls, json_obj:dict=None, json_str:str=None):
        """
        Instantiates and returns an object from json_str.
        Only those attributes of the instance is set that are found in the json_str.

        Matching is case-sensitive. Also, the camelCase keys in json_str are converted to
        snake_case before matching.

        Args:
            json_str (str) - string representation of a JSON object. Provided by Micrsoft 
            Graph API.

            json_obj (dict) - json as dictionary. Use either json_str or json_obj.

        """

        if json_obj is None and json_str is None:
            raise Exception('At least one of the optional arguments must be provided.')

        obj = cls()
        j_obj = json_obj

        if j_obj is None:
            j_obj = json.loads(s=json_str)
            
        # camel to snake
        for key in list(j_obj.keys()):
            new_key = cls._camel_to_snake(key)
            j_obj[new_key] = j_obj.pop(key)

        keys_in_json = j_obj.keys()
        keys_in_obj = obj.__dict__.keys()
        common_keys = list(set(keys_in_obj) & set(keys_in_json))
        
        for key in common_keys:
            obj.__dict__[key] = j_obj[key]

        return obj


    @classmethod
    def _camel_to_snake(cls, s):
        """ Converts camel case to snake case. """
        return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')
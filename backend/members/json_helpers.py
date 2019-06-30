class DataFormatMisMatch(ValueError):
    status_code = 400

    def __init__(self, message, status_code=None):
        """
        Helper Exception for returning proper error code to response.
        :param message: error message
        :param status_code: HTTP status code
        """
        ValueError.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        rv['code'] = self.status_code
        return rv


class InvalidInputJson(ValueError):
    status_code = 400

    def __init__(self, message, status_code=None):
        """
        Helper Exception for returning proper error code to response.
        :param message: error message
        :param status_code: HTTP status code
        """
        ValueError.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        rv['code'] = self.status_code
        return rv


class JsonRequest(object):
    """
    Base class for incoming request
    """
    MODEL = dict()

    def from_json(self, input_json, model=None):
        if model is None:
            model = self.MODEL
        for key, value in model.items():
            if type(value) == dict:
                self.from_json(input_json, model=model[key])
            else:
                if key not in input_json:
                    raise InvalidInputJson("Key {k} not in input json".format(k=key))
                self.__dict__[key] = input_json[key]

    def to_json(self, model=None):
        """
        Generates a dictionary according to the MODEL schema with class values
        :param model: Dictionary model for data
        :return: Dictionary
        """
        if model is None:
            model = self.MODEL
        json_dict = dict()
        for key, value in model.items():
            if type(value) == dict:
                json_dict[key] = self.to_json(model[key])
            elif type(self.__dict__[key]) != value:
                raise DataFormatMisMatch("Key {key} requires type {type} but type {actual} was found!".format(key=key,
                                                                                                      type=value,
                                                                                                      actual=type(self.__dict__[key])))
            else:
                json_dict[key] = self.__dict__[key]
        return json_dict

    def validate(self, model=None):
        """
        Validates Schema of request to ensure proper schema. Defined by Model
        :param model: Dictionary model for data
        :return:
        """
        if model is None:
            model = self.MODEL
        for key, value in model.items():
            if type(value) == dict:
                self.validate(model[key])
            elif type(self.__dict__[key]) != value:
                raise DataFormatMisMatch("Key {key} requires type {type} but type {actual} was found!".format(key=key,
                                                                                                      type=value,
                                                                                                      actual=type(self.__dict__[key])))
            else:
                # Passes Validation
                pass
        return

    def update(self, new_values, model=None):
        """
        Updates value of this class with input dictionary
        :param new_values: Dictionary of values to be updated
        :param model: Dictionary model for data
        :return:
        """
        if model is None:
            model = self.MODEL
        for key, value in new_values.items():
            if model.get(key) is None:
                raise DataFormatMisMatch("Key {key} not found in model!".format(key=key))
            if type(value) == dict:
                self.update(value, model[key])
            else:
                self.__dict__[key] = value
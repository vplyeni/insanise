class mongo_model:
    def get_attributes(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]

    def to_dict(self):
        dic = {}
        for i in self.get_attributes():
            dic[i] = getattr(self, i)
            """
            if isinstance(dic[i], dict):
                dic[i] = dic[i]
                del dic[i]
            """

        return dic

    def __init__(self):
        for i in self.get_attributes():
            setattr(self, i, None)


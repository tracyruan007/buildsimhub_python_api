from .model_action import ModelAction

'''
Measures to add overhangs to the model

if the model has overhang, it will change the overhangs depth
to the specified values
if the mode has no overhang, it will add overhang with the specified 
depth.

This measure applies to windows for South orientation

'''


class ShadeOverhangSouth(ModelAction):
    # this shows the ip to si conversion rate
    # if unit is 'ip', then multiply this rate.
    # for ft to meter
    # The conversion will change ft to m if ip shows
    CONVERSION_RATE = 3.28084

    def __init__(self, unit="si"):
        ModelAction.__init__(self, 'window_overhang_s', unit)

    def get_num_value(self):
        return ModelAction.num_of_value(self)

    def set_datalist(self, datalist):
        if ModelAction.unit(self) == 'ip':
            for i in range(len(datalist)):
                datalist[i] = datalist[i] / ShadeOverhangSouth.CONVERSION_RATE
        ModelAction.set_datalist(self, datalist)

from dice_tools import *
import os
import sys
import traceback

from dice_display import DiceDisplay

from OCC import StlTransfer, StlMesh
from OCC.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Visualization import Tesselator

class PythonOCC(Application):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if os.path.exists(self.config_path('script.py')):
            with open(self.config_path('script.py')) as f:
                self.__script = f.read()
        else:
            with open('template.py') as f:
                self.__script = f.read()
        self.__vis = DiceDisplay()

    saveRequest = diceSignal()
    error = diceSignal("QString", arguments=["error"])

    def output_types_changed(self, output_types):
        self.__outputs = output_types
        self.output_type_changed()
        
    def input_changed(self, input_data):
        for parameters in input_data.get('parameters', {}).values():
            self.__parameters = parameters
            break
        else:
            self.__parameters = []
        self.run_script()

    @diceProperty('QVariant')
    def vis(self):
        return self.__vis

    @diceProperty('QString')
    def script(self):
        return self.__script

    @script.setter
    def script(self, value):
        self.__script = value

    @diceSlot('QString')
    def save(self, script):
        self.__script = script
        with open(self.config_path('script.py'), 'w') as f:
            f.write(self.__script)
        self.set_output_types(self.__outputs)
        self.run_script()

    @diceTask('runOCC')
    def run_occ(self):
        return self.run_script(True)

    output_type_changed = diceSignal()

    @diceProperty('QString', name='outputType', notify=output_type_changed)
    def output_type(self):
        for v in self.__outputs:
            return v
        return ''

    @output_type.setter
    def output_type(self, value):
        if value:
            self.__outputs = [value]
        else:
            self.__outputs = []
        self.output_type_changed()


    def run_script(self, is_running=False):
        env = {}
        env.update(globals())
        if self.config_path() not in sys.path:
            sys.path.append(self.config_path())
        self.__vis.display.EraseAll()

        env['display'] = self.__vis.display
        env['parameters'] = self.__parameters
        env['app'] = self
        env['is_running'] = is_running
        try:
            try:
                exec(self.__script, env)
            except NameError as e:
                tb = sys.exc_info()[2]
                if tb.tb_next and tb.tb_next.tb_next is None:
                    error = "Error: %s\n"%e.args[0]
                    self.log(error)
                    self.error(error)
                else:
                    raise
        except:
            exc = traceback.format_exc(chain=False).split('\n')
            error = "Error:\n%s\n"%'\n'.join(exc[:1]+exc[3:])
            self.log(error)
            self.error(error)
        self.__vis.render()
        if self.output_type and 'app_output' in env:
            self.set_output(self.output_type, env['app_output'])
        return True

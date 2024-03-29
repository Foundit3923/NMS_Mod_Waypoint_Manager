
import logging
import ctypes
import pprint

import nmspy.memutils as memutils
from nmspy.data.cpptypes import std
from nmspy.data import common, enums as nms_enums
import nmspy.data.function_hooks as hooks
import nmspy.hooking as hooking
from nmspy.hooking import disable, main_loop
from nmspy.memutils import map_struct
import nmspy.data.structs as nms_structs
from nmspy.mod_loader import NMSMod
from nmspy.calling import call_function
import nmspy.data.local_types as lt
import nmspy.common as nms
from nmspy.mod_loader import ModState
from dataclasses import dataclass

"""class Vector3f(ctypes.Structure):
    x: float
    y: float
    z: float

    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("_padding", ctypes.c_byte * 0x4),
    ]

    def __str__(self) -> str:
        return f"<{self.x, self.y, self.z}>"""

""" def print_struct(struct: ctypes.Structure, depth: int = 0):
    for field_name, field_type in struct._fields_:
        if isinstance(field_type, ctypes.Structure):
            logging.info("  " * depth + field_name + ":")
            print_struct(field_type, depth + 1)
        else:
            if not field_name.startswith("_"): #for fear of mangling
                logging.info("  " * depth + f"{field_name}: {getattr(struct, field_name)}")
            else:
                # See if we have a non-private version of the field.
                if hasattr(struct, field_name[1:]):
                    logging.info("  " * depth + f"{field_name}: {getattr(struct, field_name[1:])}") """

@dataclass
class State_Vars(ModState):
    def __init__(self, binoc_arg, pEnv_arg):
        self.binoculars: binoc_arg
        self.playerEnv: pEnv_arg


def print_struct(struct: ctypes.Structure, max_depth=5):
    depth = 0
    stack = [iter(struct._fields_)]
    while stack:
        if len(stack) > max_depth:
            logging.info("Max recursion depth exceeded")
        try:
            name: str
            name, type_ = next(stack[-1])
        except StopIteration:
            stack.pop(-1)
            depth -= 1
            continue
        if isinstance(type_, ctypes.Structure):
            logging.info(" " * depth + name + ":")
            stack.append(iter(type_._fields_))
            dpeth += 1
            continue
        #check for public versions of private fields
        name = name.removeprefix('_')
        if hasattr(struct, name):
            attr = getattr(struct, name)
            logging.info(" " * depth + f"{name}:{attr}")



class function_testing(NMSMod):

    __author__ = "foundit"
    __description__ = "fucking with the mod system"
    __version__ = "0.1"
    __NMSPY_required_version__ = "0.6.0"

    state = State_Vars(         
        ctypes.Structure,
        ctypes.Structure,
    )

    def __init__(self):
        super().__init__()
        self.text: str = "mm"
        self.should_print = True
        self.lookupInt = 0

    @property
    def _text(self):
        return self.text.encode()
    
    @hooks.cGcBinoculars.SetMarker.after
    def checkSetMarker(self, this):
        try:
            #logging.info(f'Set player struct')
            #self.playerEnv = map_struct(this, nms_structs.cGcPlayerEnvironment)
            logging.info("Binoc SetMarker event triggered")
            #playerHud = map_struct(this, nms_structs.cGcPlayerHUD);
            #dat = hooks.cGcBinoculars.SetMarker.before;
            logging.info(f'memutils: ')
            logging.info(memutils.pprint_mem(this + 2000, 0x10))
            logging.info(f'print_struct(mpDiscoveryGui): ')
            #print_struct(binoculars.DiscoveryGui.contents)
            #pprint.PrettyPrinter(binoculars.DiscoveryGui.contents)
            logging.info(f'print_struct(MarkerModel.lookupInt): ')
            #print_struct(binoculars.MarkerModel.lookupInt)
            #logging.info(self.binoculars.MarkerModel.lookupInt)
            #logging.info(f'function call of previous: ')
            self.lookupInt = self.binoculars.MarkerModel.lookupInt
            #arr = ctypes.create_string_buffer(0x10)
            #ptr = ctypes.addressof(arr)
            #call_function("Engine::GetNodeAbsoluteTransMatrix", self.lookupInt, ptr)
            #mat = map_struct(ptr, common.cTkMatrix34)
            #logging.info(str(mat))
            #logging.info(f'marker pos change')
            #time.sleep(5)
            #call_function("Engine::ShiftAllTransformsForNode", lookupInt, )
            #vec = common.Vector3f(1, 0, 0) #x, y, z
            #call_function("Engine::SetNodeTransMat", self.lookupInt,  ctypes.byref(vec))
            sim_addr = ctypes.addressof(nms.GcApplication.data.contents.Simulation)
            binocs = sim_addr + 74160 + 0 + 6624           
            logging.info(f'binocs: '+str(self.state.binoculars))
            logging.info(f'this:   ' + str(this))
        except Exception as e:
            logging.exception(e)

    @hooks.cGcPlayerHUD.Update.before
    def checkPlayerHUDUpdate(self, this):
         hud = map_struct(this, nms_structs.cGcPlayerHUD)
         logging.info(f'Player HUD position event')

    #@hooking.on_key_pressed("shift+b")
    #def moveup(self):
    #    try:
    #        logging.info(f'Pressed Space, moving marker: ')
    #        vec = common.Vector3f(0,0,5) #this is not the location we want. This is how much we change each of these values
    #        call_function("Engine::ShiftAllTransformsForNode", self.lookupInt, ctypes.addressof(vec))
    #    except Exception as e:
    #        logging.exception(e)



    @hooking.on_key_pressed("o")
    def press(self):
        try:
            logging.info(f'Output')
            logging.info(ctypes.addressof(nms.GcApplication.data.contents.Simulation) - ctypes.addressof(nms.GcApplication.data.contents))
            logging.info(f'Pressed tic: ')
            #self.player = map_struct(this, nms_structs.cGcPlayer)
            #x = str(self.player.position.x)
            #y = str(self.player.position.y)
            #z = str(self.player.position.z)
            position = self.state.playerEnv.mPlayerTM
            position_matrix = position.matrix
            position_matrix_string = ','.join(str(item) for item in position_matrix)
            logging.info(f'position matrix:')
            logging.info(position_matrix_string)
            #arr = ctypes.create_string_buffer(0x10)
            #ptr = ctypes.addressof(arr)
            #call_function("Engine::GetNodeAbsoluteTransMatrix", self.lookupInt, ptr)
            #mat = map_struct(ptr, common.cTkMatrix34)
            logging.info(f'positoin __str__')
            logging.info(str(position))
        except Exception as e:
            logging.exception(e)

    @hooking.on_key_pressed("space")
    def press(self):
        logging.info(f'this isn\'t possible')
        try:
            address = ctypes.addressof(self.state.binoculars)
            logging.info(f'ctypes.addressof(self.state.binoculars): ' + str(address))
            offset = ctypes.addressof(self.state.binoculars)
            ptr = ctypes.c_ulonglong(offset)
            call_function("cGcBinoculars::SetMarker", ctypes.addressof(ptr))
        except Exception as e:
            logging.exception(e)

    @hooking.on_state_change("APPVIEW")
    def init_state_var(self):
        logging.info(f'state var set')
        #Isn't set until after save file is fully loaded
        self.state.playerEnv = nms.GcApplication.data.contents.Simulation.environment.playerEnvironment        
        sim_addr = ctypes.addressof(nms.GcApplication.data.contents.Simulation)
        self.state.binoculars = map_struct(sim_addr + 74160 + 6624, nms_structs.cGcBinoculars)
        



    #@hooking.on_key_pressed("alt")
    #def press(self):
    #    try:
    #        logging.info(f'Pressed Space, moving marker: ')
    #        vec = common.Vector3f(3,0,0) #this is not the location we want. This is how much we change each of these values
    #        call_function("Engine::ShiftAllTransformsForNode", self.lookupInt, ctypes.addressof(vec))
    #    except Exception as e:
    #        logging.exception(e)

    #@hooking.on_key_pressed("space")
    #def press(self):
    #    try:
    #        logging.info(f'Pressed Space, moving marker: ')
    #        vec = common.Vector3f(1, 2, 3)
    #        call_function("Engine::ShiftAllTransformsForNode", self.lookupInt, ctypes.POINTER(vec))
    #    except Exception as e:
    #        logging.exception(e)

    #@hooks.cGcBinoculars.GetRange.before
    #def checkGetRange(self, this):
    #    logging.info("Binoc GetRange event triggered")

    #@hooks.cGcBinoculars.GetScopeMatrix.before
    #def checkGetScopeMatrix(self):
    #    logging.info("Binoc GetScopeMatrix event triggered")

    #@hooks.cGcBinoculars.UpdateTarget.before
    #def checkBinocUpdateTarget(self, this, float ):
    #    logging.info("Binoc Update Target event triggered")

    #@hooks.cGcBinoculars.UpdateDataView.before
    #def checkBinocUpdateDataView(self, this, cGcNGuiLayer, DiscoveryResolver, bool):
    #    logging.info("Binoc UpdateDataView event triggered")

    @hooks.cGcBinoculars.UpdateDiscoveryUI.before
    def checkBinocUpdateDiscoveryUI(self):
        logging.info("Binoc UpdateDiscoveryUI event triggered")

    #@hooks.cGcBinoculars.SetSystemScanData.before
    #def checkBinocSetSystemScanData(self):
    #    logging.info("Binoc SetSystemScanData event triggered")

    #@hooks.cGcBinoculars.LoadGui.before
    #def checkBinocLoadGui():
    #    logging.info("Binoc LoadGui event triggered")

    @hooks.cGcPlayer.GetPosition.after
    def checkPlayerGetPosition():
        logging.info("Player GetPosition event triggered")

    #@hooks.cGcPlayer.IsUsingJetpack.before
    #def checkPlayerIsUsingJetpack():
    #    logging.info("Player IsUsingJetpack event triggered")

    #@hooks.cGcPositionMarker.SetTarget.before
    #def checkPositionMarkerSetTarget(self):
    #    logging.info("Position Marker SetTarget event triggered")

    #@hooks.cGcPositionMarker.Render.before
    #def checkPositionMarkerRender(self):
    #    logging.info("Position Marker Render event triggered")

    #@hooks.nvgText
    #def change_test(self, ctx, x: float, y: float, string, end):
    #    if string == b"Options":
    #        string = ctypes.c_char_p(b"Hi")
    #        call_function("nvgText", ctx, x + 30, y, ctypes.c_char_p(self._text), end)
    #    return hooks.nvgText.original(ctx, x, y, string, end)

    # @nvgText.before
    # def change_test_after(self, ctx, x: float, y: float, string, end):
    #     # logging.info("change_test")
    #     logging.info(string)
    #     # logging.info(self._text)
    #     if string == b"Options":
    #         string = ctypes.c_char_p(b"Hi")
    #         call_function("nvgText", ctx, x + 30, y, ctypes.c_char_p(self._text), end)
    #     logging.info("about to return")
    #     return (ctx, x, y, string, end)

    # @hook_function("nvgEndFrame")
    # class nvgHook(NMSHook):
    #     def detour(self, ctx):
    #         # Draw something somewhere
    #         call_function("nvgBeginPath", ctx)
    #         call_function("nvgRect", ctx, 100, 100, 100, 100)
    #         colour = nms_structs.NVGColor(r=1, g=0, b=0, a=1)
    #         colour_addr = ctypes.addressof(colour)
    #         logging.info(colour_addr)
    #         call_function("nvgFillColor", ctx, colour_addr)
    #         call_function("nvgFill", ctx)
    #         logging.info("Drew a rectangle?")
    #         ret = self.original(ctx)
    #         logging.info(f"nvgEnd: ctx: {ctx}")
    #         return ret

    #@hooks.cGcPlanet.SetupRegionMap.after
    #@disable
    #def detour(self, this):
    #    logging.info(f"cGcPlanet*: {this}")
    #    planet = map_struct(this, nms_structs.cGcPlanet)
    #    logging.info(f"Planet {planet.planetIndex} name: {planet.planetData.name}")

    # @cGcPlanet.SetupRegionMap
    # def setup_regions(self, this):
    #     logging.info(f"cGcPlanet*: {this}")
    #     ret = cGcPlanet.SetupRegionMap.original(this)
    #     planet = map_struct(this, nms_structs.cGcPlanet)
    #     logging.info(f"Planet {planet.planetIndex} name: {planet.planetData.name}")
    #     return ret

    #@hooks.main_loop.before
    #def do_something(self, this):
    #    logging.info("Get player")
    #    self.player = map_struct(this, nms_structs.cGcPlayer)

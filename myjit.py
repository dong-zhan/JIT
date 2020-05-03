from ctypes import c_int, WINFUNCTYPE, windll, CFUNCTYPE
from ctypes.wintypes import HWND, LPCWSTR, UINT
prototype = WINFUNCTYPE(c_int, HWND, LPCWSTR, LPCWSTR, UINT)  #TODO: what's this for? this defines prototype
#paramflags first in tuple: 1 input, 2 output, 4 input defaults to 0
#paramflags second in tuple: parameter name
#paramflags third in tuple: The optional third item is the default value for this parameter.
paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", "Hello from ctypes"), (1, "flags", 0)
MessageBoxW = prototype(("MessageBoxW", windll.user32), paramflags)

from ctypes.wintypes import LPVOID, DWORD, DWORD        #SIZE_T not defined
prototype = WINFUNCTYPE(LPVOID, LPVOID, DWORD, DWORD, DWORD)
paramflags = (1, "address", 0), (1, "size", 0), (1, "alloc_type", 0), (1, "protect_flag", 0)
VirtualAlloc = prototype(("VirtualAlloc", windll.kernel32), paramflags)

prototype = WINFUNCTYPE(LPVOID, LPVOID, DWORD, DWORD)
paramflags = (1, "address", 0), (1, "size", 0), (1, "type", 0)
VirtualFree = prototype(("VirtualFree", windll.kernel32), paramflags)

prototype = WINFUNCTYPE(LPVOID, LPVOID, LPVOID, DWORD)
paramflags = (1, "dest", 0), (1, "src", 0), (1, "size", 0)
RtlMoveMemory = prototype(("RtlMoveMemory", windll.kernel32), paramflags)

class bytesInMachineCodeSpace :
    def __init__(self, size):
        PAGE_EXECUTE_READWRITE = 0x40  
        MEM_COMMIT = 0x1000    
        self.size = size
        self.ptr = VirtualAlloc(0, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE)        
    def copy_to_sys(self, python_bytes):
        src = ctypes.create_string_buffer(python_bytes)     #python byte buffer -> c buffer
        lenSrc = len(python_bytes)
        if lenSrc > self.size:
            return
        RtlMoveMemory(self.ptr, src, lenSrc)
    def copy_from_sys(self):
        dest = ctypes.create_string_buffer(self.size)
        RtlMoveMemory(dest, self.ptr, self.size)
        return dest
    def __del__(self):
        MEM_COMMIT = 0x1000    
        VirtualFree(self.ptr, self.size, MEM_COMMIT)
        
code = bytes([0x8b, 0x44, 0x24, 0x04, 0x03, 0x44, 0x24, 0x08, 0xc3])     #32bits from dumpbin's raw data   dumpbin ...obj /all
#code = bytes([0x67, 0x8b, 0x44, 0x24, 0x04, 0x67, 0x03, 0x44, 0x24, 0x08, 0xc3])       #64bits
bs = bytesInMachineCodeSpace(20)
bs.copy_to_sys(code)
abs = bs.copy_from_sys()
#print(sizeof(abs), repr(abs.raw))
dump_raw_data(abs)

prototype = CFUNCTYPE(DWORD, DWORD, DWORD) #WINFUNCTYPE
#paramflags = (1, "dest", 0), (1, "src", 0)
add = prototype(bs.ptr)

#add = prototype(bs.ptr)
add.restype = DWORD
add.argtypes = [DWORD, DWORD]

def dump_raw_data(code):
    lencode = len(code)
    text = []
    for i in range(lencode):
        text.append(hex(code.raw[i]))
    print(text)

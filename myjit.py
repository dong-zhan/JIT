def imps():
    global ctypes, c_int, WINFUNCTYPE, windll, CFUNCTYPE, LPVOID, DWORD, VirtualAlloc, VirtualFree, RtlMoveMemory, c_int64
    
    import ctypes
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
        
def dump_machine_code_c_char_array(code):
    lencode = len(code)
    text = []
    for i in range(lencode):
        text.append(hex(code.raw[i]))
    print(text)
	
def dump_machine_code(code):
    lencode = len(code)
    text = []
    for i in range(lencode):
        text.append(hex(code[i]))
    print(text)
    
#RAW DATA #1
#  00000000: 48 83 EC 08 48 8B 44 24 08 48 03 44 24 10 48 83  H.?H.D$.H.D$.H.
#  00000010: C4 08 C3   
  

def hexString_to_bytes(hs):
    dest = b''
    for e in hs :
        dest += int(e, 16).to_bytes(1, byteorder='big')
    return dest
  
def test(x86 = False):     
    global add, bs, abs, code
    if x86 :
        #32bits from dumpbin's raw data   dumpbin ...obj /all
        code = bytes([0x8b, 0x44, 0x24, 0x04, 0x03, 0x44, 0x24, 0x08, 0xc3])    
    else :
        #64bits
        code = '48 83 EC 08 48 89 C8 48 01 D0 48 83 C4 08 C3'
        code = code.split(' ')
        code = hexString_to_bytes(code)
    bs = bytesInMachineCodeSpace(20)
    bs.copy_to_sys(code)
    abs = bs.copy_from_sys()
    dump_machine_code_c_char_array(abs)
    if x86 :
        #32bits
        prototype32 = CFUNCTYPE(DWORD, DWORD, DWORD) #WINFUNCTYPE
        #paramflags = (1, "dest", 0), (1, "src", 0)
        add = prototype32(bs.ptr)
    else :
        prototype64 = CFUNCTYPE(c_int64, c_int64, c_int64) #WINFUNCTYPE
        #paramflags = (1, "dest", 0), (1, "src", 0)
        add = prototype64(bs.ptr)

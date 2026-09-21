from dirs import *

#### COMPUTE ###

def compute_sources() -> list:
    rtl_dirs = get_rtl_from(COMPUTE_DIR / 'rtl')
    return rtl_dirs

def compute_toplevel() -> str:
    toplevel = "cordic"
    print(f"Top Level Entity is set to '{toplevel}'")
    return toplevel

#### MEMORY ###

def memory_sources() -> list:
    rtl_dirs = []
    rtl_dirs.extend(get_rtl_from(MEMORY_DIR / 'rtl'))
    rtl_dirs.extend(get_rtl_from(MEMORY_DIR / 'dv' / 'altera'))
    rtl_dirs.extend(get_rtl_from(MEMORY_DIR / 'dv' / 'env'))
    return rtl_dirs

def memory_toplevel() -> str:
    toplevel = "tb_top"
    print(f"Top Level Entity is set to '{toplevel}'")
    return toplevel

### MAIN EXPORT ###

def get_sources_for(tb_top:str = None):
    if tb_top == "compute":
        return compute_sources(), compute_toplevel()
    elif tb_top == "memory":
        return memory_sources(), memory_toplevel()
        
    raise ValueError(f"tb_top = '{tb_top}' doesnt have sources defined!")

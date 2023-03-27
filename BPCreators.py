from typing import Dict

__INDENT = "   "

TEXT_PACKAGE_KEY = "35D222FF48C4C980DA5D309BE0C26579"

def IndentContent(Content=[]):
    return tuple(__INDENT + x for x in Content)

def Object(Class=None, Name="", Content=[]):
    header = "Begin Object"
    if Class is not None:
        header += f' Class={Class}'
    header += f' Name="{Name}"'
    return (
        header,
        *IndentContent(Content),
        f'End Object'
    )

def ArrayItem(ArrayName="", ArrayIndex=0, Value=""):
    return f'{ArrayName}({ArrayIndex})={Value}'

def ReferenceFromTypeName(widget):
    return f"{widget['Type']}'\"{widget['Name']}\"'"

def PropertiesToString(**props : Dict[str, str]):
    return tuple(f'{key}={value}' for key, value in props.items())

def Text(props : dict):
    if "CultureInvariantString" in props: return f'INVTEXT("{props["CultureInvariantString"]}")'
    else: return f'NSLOCTEXT("[{TEXT_PACKAGE_KEY}]", "{props["Key"]}", "{props["SourceString"]}")'

def StrValue(key, v):
    if "::" in v:
        return v.split("::")[-1]
    if key in ("DisplayLabel",):
        return f'"{v}"'
    return v

def __StructValue(key, v):
    if isinstance(v, str): return StrValue(key, v)
    else: return f'{v}'

def Struct(props : dict):
    pairs = (
        f'{key}={__StructValue(key, value)}' for key, value in props.items()
    )
    return f'({",".join(pairs)})'
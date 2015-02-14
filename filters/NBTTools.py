from collections import Mapping, Sequence
from pymclevel.nbt import (TAG_Value,
                           TAG_Compound, TAG_List,
                           TAG_String,
                           TAG_Byte, TAG_Short, TAG_Int, TAG_Long,
                           TAG_Float, TAG_Double,
                           TAG_Byte_Array, TAG_Int_Array)

def NBTCompound(**kwargs):
    tag = TAG_Compound()
    for key in kwargs:
        tag[str(key)] = NBT(kwargs[key])
    return tag

def NBTList(*args):
    tag = TAG_List()
    for arg in args:
        tag.append(NBT(arg))
    return tag

def NBT(v=None, **kwargs):
    if v is None:
        return NBTCompound(**kwargs)
    elif isinstance(v, TAG_Value):
        return v
    elif isinstance(v, int):
        return TAG_Int(v)
    elif isinstance(v, float):
        return TAG_Float(v)
    elif isinstance(v, basestring):
        return TAG_String(v)
    elif isinstance(v, Mapping):
        return NBTCompound(**v)
    elif isinstance(v, Sequence):
        return NBTList(*v)
    else:
        raise TypeError("Don't know how to convert {0} to NBT".format(v))

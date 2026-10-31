# Native GetClass is authoritative: connectivity may return a PCB_VIA as a PCB_TRACK Python wrapper.
def native_via_layers(item,layers):
 if item.GetClass()!='PCB_VIA':return []
 return [layer for layer in layers if item.IsOnLayer(layer)]

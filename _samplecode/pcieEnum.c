
push BUS_0 to bus_stack

while bus_stack != NULL:
    bus = pop(bus_stack)
    while find_next_sw(bus) is true:
        child.prim_bus = bus.prim_bus
        child.second_bus = bus.prim_bus+1
        child.subord_bus = bus.second_bus
        push(child)
    // find an EP
    update_subord_bus(bus_stack)

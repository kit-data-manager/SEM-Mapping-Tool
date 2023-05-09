try:
    from dateutil import parser
except:
    print("dateutil not found")
try:
    import numpy as np
except:
    print("numpy not found, dateutil not found")
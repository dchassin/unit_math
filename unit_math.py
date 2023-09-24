import copy
import re

TAGS = ["c","e","h","k","m","s","scale","offset","prec"]
UNITS = {
    "unit" : [0,0,0,0,0,0,1,0,16],
    "m" : [-1,0,1,0,-1,0,4.121487e01,0,7],
    "kg" : [0,0,0,0,1,0,1.09775094e30,0,10],
    "s" : [-2,0,1,0,-1,0,1.235591e10,0,7],
    "A" : [2,1,-1,0,1,0,5.051397e08,0,7],
    "K" : [2,0,0,-1,1,0,1.686358e00,0,7],
    "cd" : [4,0,-1,0,2,0,1.447328E+00,0,7],
    "$" : [0,0,0,0,1,1,1.097751e30,0,7],
}
SCALARS = {
    "Y" : 24,
    "Z" : 21,
    "E" : 18,
    "P" : 15,
    "T" : 12,
    "G" : 9,
    "M" : 6,
    "k" : 3,
    "h" : 2,
    "da" : 1,
    "d" : -1,
    "c" : -2,
    "m" : -3,
    "u" : -6,
    "n" : -9,
    "p" : -12,
    "f" : -15,
    "a" : -18,
    "z" : -21,
    "y" : -24,
}
SPECS = {
    "pi" : "3.1415926536 unit",
    "rad" : "0.159155 unit",
    "deg" : "0.0027777778 unit",
    "grad" : "0.0025 unit",
    "quad" : "0.25 unit",
    "sr" : "0.5 rad",

    #  Derived SI
    "R" : "0.55555556 K",
    "degC" : "K-273.14",
    "degF" : "R-459.65",
    "N" : "1 m.kg/s^2",
    "Pa" : "1 N/m^2",
    "J" : "1 N.m",

    #  Time
    "min" : "60 s",
    "h" : "60 min",
    "day" : "24 h",
    "wk" : "7 day",
    "yr" : "365 day",
    "syr" : "365.24 day",

    #  Length
    "in" : "0.0254 m",
    "ft" : "12 in",
    "yd" : "3 ft",
    "mile" : "5280 ft",

    #  Area
    "sf" : "1 ft^2",
    "sy" : "1 yd^2",
    "ha" : "10000 m^2",

    #  Volume
    "cf" : "1 ft^3",
    "cy" : "1 yd^3",
    "gal" : "0.0037854118 m^3",
    "l" : "0.001 m^3",

    #  Mass
    "lb" : "0.453592909436 kg",
    "tonne" : "1000 kg",

    #  Velocity
    "mph" : "1 mile/h",
    "fps" : "1 ft/s",
    "fpm" : "1 ft/min",
    "mps" : "1 m/s",
    "knot" : "1.151 mph",

    #  Flow rates
    "gps" : "1 gal/s",
    "gpm" : "1 gal/min",
    "gph" : "1 gal/h",
    "cfm" : "1 ft^3/min",
    "ach" : "1 unit/h",

    #  Frequency
    "Hz" : "1 unit/s",

    #  EM units
    "W" : "1 J/s",
    "Wh" : "1 W.h",
    "Btu" : "0.293 W.h",
    "ton" : "12000 Btu/h", #  ton cooling
    "tons" : "1 ton.s ", #  ton.second cooling
    "tonh" : "1 ton.h ", #  ton.hour cooling
    "hp" : "746 W ", #  horsepower
    "V" : "1 W/A ", #  Volt
    "C" : "1 A.s ", #  Coulomb
    "F" : "1 C/V ", #  Farad
    "Ohm" : "1 V/A ", #  resistance
    "H" : "1 Ohm.s ", #  Henry
    "VA" : "1 V.A  ", #  Volt-Amp
    "VAr" : "1 V.A   ", #  Volt-Amp reactive
    "VAh" : "1 VA.h",
    "Wb" : "1 J/A ", #  Weber
    "lm" : "1 cd.sr ", #  lumen
    "lx" : "1 lm/m^2 ", #  lux
    "Bq" : "1 unit/s ", #  Becquerel
    "Gy" : "1 J/kg ", #  Grey
    "Sv" : "1 J/kg ", #  Sievert
    "S" : "1 unit/Ohm ", #  Siemens

    #  data
    "b" : "1 unit ", #  1 bit
    "B" : "8 b ", #  1 byte

    #  pressure
    "bar" : "100000 Pa",
    "psi" : "6894.757293178 Pa",
    "atm" : "98066.5 Pa",
    "inHg" : "3376.85 Pa ", #  at 60degF
    "inH2O" : "248.843 Pa ", #  at 60degF

    # other energy
    "EER" : "1 Btu/Wh",
    "ccf" : "1000 Btu",  #  this conflict with centi-cubic-feet (ccf)
    "therm" : "100000 Btu",
}

def get_unit(unit):
    if not unit in UNITS:
        for prefix, scale in SCALARS.items():
            if unit.startswith(prefix) and unit[len(prefix):] in UNITS:
                UNITS[unit] = UNITS[unit[len(prefix):]].copy()
                UNITS[unit][6] *= 10**scale
                break
    if not unit in UNITS:
        UNITS[unit] = derive(unit,"1 "+unit)
    return UNITS[unit]

def derive(unit,spec):
    try:
        scale, defn = spec.strip().split(" ")
        offset = 0
        scale = float(scale)
        prec = 7
    except:
        defn, offset = spec.strip().split("-")
        scale = 1
        offset = -float(offset)
        prec = 2
    if "/" in defn:
        num,den = re.split("/",defn)
    else:
        num = defn
        den = "unit"
    args = UNITS["unit"][:6]
    for item in num.split("."):
        expn = 1
        if "^" in item:
            item,expn = item.split("^")
        u = get_unit(item)
        for n,m in enumerate(u[:6]):
            args[n] += m*int(expn)
        scale *= u[6]
    for item in den.split("."):
        expn = 1
        if "^" in item:
            item,expn = item.split("^")
        u = get_unit(item)
        for n,m in enumerate(u[:6]):
            args[n] -= m*int(expn)
        scale /= u[6]
    args.extend([scale,offset,prec])
    return args

for unit,spec in SPECS.items():
    UNITS[unit] = derive(unit,spec)

class UnitException(Exception):
    pass

class Unit(str):

    def __new__(self,unit):
        return super().__new__(self,unit)

    def __init__(self,unit):
        self.unit = unit
        spec = get_unit(unit)
        self.args = spec[:6]
        self.scale = spec[6]

    def matches(self,x,exception=False):
        if self.args == x.args:
            return True
        if not exception:
            return False
        raise UnitException("units do not match")

class floatUnit:

    def __init__(self,value,unit=None):
        if type(value) is str and " " in value:
            value,unit = value.split()
        self.unit = Unit(unit) if unit else None
        self.value = float(value)

    def __str__(self):
        return f"{self.value:g} {self.unit}"

    def __add__(self,x):
        self.unit.matches(x.unit,True)
        return floatUnit(self.value+x.value/self.unit.scale*x.unit.scale,self.unit)

    def __sub__(self,x):
        self.unit.matches(x.unit,True)
        return floatUnit(self.value-x.value/self.unit.scale*x.unit.scale,self.unit)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __complex__(self):
        return complex(self.value)
        
    def __mul__(self,x):
        pass

    def __truediv__(self,x):
        pass

    def __mod__(self,x):
        pass

    def __pow__(self,x):
        pass

    def __lt__(self,x):
        pass

    def __gt__(self,x):
        pass

    def __le__(self,x):
        pass

    def __ge__(self,x):
        pass

    def __eq__(self,x):
        pass

    def __ne__(self,x):
        pass

x = floatUnit("1.23 m")
print("x =",x)
y = floatUnit("1 cm")
print("y = ",y)
print("x+y =",x+y)
print("x-y =",x-y)

p = floatUnit(1,"kWh") + floatUnit(1,"MJ")
print(p)

print(UNITS['s'],UNITS['min'],UNITS['h'])

import sys, imp, re, os
from pymclevel import mclevel

def normalizeFilterOptionName(name):
    return re.sub(r'\s+', '-', name.lower())

def importFilter(path):
    name = os.path.basename(path)
    if name.endswith('.py'):
        name = name[:-3]
    return imp.load_source(name, path)

def importFilterOptions(filterModule):
    opts = {}
    if hasattr(filterModule, 'inputs'):
        for option in filterModule.inputs:
            if len(option) < 2:
                defaultValue = None
            elif isinstance(option[1], tuple):
                defaultValue = option[1][0]
            else:
                defaultValue = option[1]

            opts[normalizeFilterOptionName(option[0])] = (option[0], defaultValue)
    return opts

def parseFilterOptions(argv, filterOptionsDef):
    mapPaths = []
    filterOptions = {}

    for arg in argv:
        m = re.match(r'^(\S+)=(.+)$', arg)
        if m:
            optionKey = normalizeFilterOptionName(m.group(1))
            if optionKey not in filterOptionsDef:
                raise SystemExit(1, "Filter has no option named '{0}'".format(m.group(1)))

            optionValue = eval(m.group(2))

            filterOptions[filterOptionsDef[optionKey][0]] = optionValue
        else:
            mapPaths.append(arg)

    for optionKey in filterOptionsDef:
        optionName, optionDefault = filterOptionsDef[optionKey]
        if optionName not in filterOptions and optionDefault is not None:
            filterOptions[optionName] = optionDefault

    return mapPaths, filterOptions

def loadMaps(mapPaths):
    for mapPath in mapPaths:
        yield mclevel.fromFile(mapPath)

def applyFilter(filterModule, level, **filterOptions):
    filterModule.perform(level, level.bounds, filterOptions)

def main(argv):
    if len(argv) < 3:
        print "Usage: <filter> [filter options] <map>..."
    else:
        filterModule = importFilter(argv[1])
        filterOptionsDef = importFilterOptions(filterModule)
        print "Applying filter {0}".format(filterModule.__name__)

        mapPaths, filterOptions = parseFilterOptions(argv[2:], filterOptionsDef)
        for optionName in filterOptions:
            print "  {0} = {1}".format(optionName, repr(filterOptions[optionName]))

        for level in loadMaps(mapPaths):
            print "Processing map {0}".format(level.worldFolder.filename)
            applyFilter(filterModule, level, **filterOptions)
            level.saveInPlace()

if __name__ == "__main__":
    main(sys.argv)
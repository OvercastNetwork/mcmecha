from urllib2 import urlopen
from uuid import UUID
import json
from NBTTools import NBT, NBTList

ProfileCache = {}

def normalizeUsername(name):
    return name.strip().lower()

def uuidFromUsername(name, time=1422921600):
    try:
        return json.load(urlopen("https://api.mojang.com/users/profiles/minecraft/{0}?at={1}".format(name, time)))['id']
    except Exception as ex:
        print "Can't get a UUID for username {0}: {1}".format(name, repr(ex))

def profileFromUuid(uuid):
    try:
        return json.load(urlopen("https://sessionserver.mojang.com/session/minecraft/profile/{0}?unsigned=false".format(uuid)))
    except Exception as ex:
        print "Can't get a profile for UUID {0}: {1}".format(uuid, repr(ex))

def profileFromUsername(name):
    name = normalizeUsername(name)

    if name in ProfileCache:
        return ProfileCache[name]
    else:
        uuid = uuidFromUsername(name)
        if uuid:
            profile = profileFromUuid(uuid)
            if profile:
                ProfileCache[name] = profile
                return profile

def profileJSONtoNBT(json):
    tag = NBT(Id=str(UUID(json['id'])), Name=json['name'])

    if json['properties']:
        tag['Properties'] = nbtProps = NBT()
        for jsonProp in json['properties']:
            name = jsonProp['name']
            nbtProp = NBT(Value=jsonProp['value'])
            if jsonProp['signature']:
                nbtProp['Signature'] = NBT(jsonProp['signature'])

            if name not in nbtProps:
                nbtProps[name] = NBTList()
            nbtProps[name].append(nbtProp)

    return tag

inputs = [
    ('Convert all', False),
    ('Clear cache', True)
]

def perform(level, box, options):
    convertAll = options['Convert all']
    clearCache = options['Clear cache']

    if clearCache:
        ProfileCache.clear()

    for chunk, slices, point in level.getChunkSlices(box):
        for skull in chunk.getTileEntitiesInBox(box):

            # if skull['id'].value == 'Skull':
            #     print skull

            if skull['id'].value == 'Skull' and skull.get('ExtraType') and (convertAll or not skull.get('Owner')):
                username = skull.get('ExtraType').value
                print "Updating head of '{0}' at {1}, {2}, {3}".format(username, skull['x'].value, skull['y'].value, skull['z'].value)

                profile = profileFromUsername(username)
                if profile:
                    skull['Owner'] = profileJSONtoNBT(profile)
                    chunk.dirty = True
                else:
                    print "Failed to get profile for {0}".format(username)

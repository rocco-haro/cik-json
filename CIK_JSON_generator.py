import requests

class CIKJSONGenerator(object):
    def __init__(self):
        print("starting...")
        self.reportKeys = []
        self.frankenstienJSON = {}

    def fetchAllCIKs(self):
        r = requests.get('https://wsbnports.azurewebsites.net/odata/nports/FilerCiks')
        self.ciks = r.json()['value']

    def fetchCIKData(self):
        data = {}
        keyCount = []
        total = len(self.ciks)
        count = 0
        for cik in self.ciks:
            url = "https://wsbnports.azurewebsites.net/odata/nports('{}')?$count=true".format(cik)
            r = requests.get(url)
            try:
                cikInfo = r.json()['value']
                data[cik] = cikInfo
                for report in cikInfo:
                    self.unravelJSON(report, 'root')
                print("{0}/{1}".format(count, total), cik)
                count+=1
            except:
                continue
        # print(self.frankenstienJSON)

    def countUniqueNodes(self, dic):
        key_set = set()
        for keys, _v in dic.items():
            key_split = keys.split("-")
            possible_keys = self.getPossibleKeys
            key_set.add(keys)
        print("Unique nodes:", len(key_set))

    def parseKeysForCIK(self):
        url = "https://wsbnports.azurewebsites.net/odata/nports('0000081443')?$count=true"
        r = requests.get(url)
        data = r.json()['value']
        keyCount = []
        for report in data:
            #print(report.keys())
            #self.iterdict(report)
            #print(self.reportKeys)
            self.unravelJSON(report, 'root')
            keyCount.append(len(self.frankenstienJSON.keys()))

        # for k, v in self.frankenstienJSON.items():
        #     print(k, v)
        # self.countUniqueNodes(self.frankenstienJSON)
       # print(self.frankenstienJSON)

    def writeValue(self, nextKeys, dicRef, value):
        # search for a record of the first key. If not found, create it & perhaps assign the value
        # once found, check it's value and look for a dict that has the next key
        # if the next key is not found, create it. 

        # repeat until the last key, and write the value
        curr_key = nextKeys[0]
        if curr_key not in dicRef.keys(): # key does not exist
            if len(nextKeys[1:]) == 0:
                dicRef[curr_key] = value # create and assign - done.
                return 
            dicRef[curr_key] = {} # just create
            self.writeValue(nextKeys[1:], dicRef[curr_key], value)
        else:
            # the key exists
            key_values = dicRef[curr_key]
            # what is key values?
            # a single value, a dictionary, or an array
            if len(nextKeys) > 1:
                next_key, leftover_keys = nextKeys[1], nextKeys[2:]
                # if 'monthlyReturnCats' in nextKeys:
                #     print("curr_key: {0}".format(curr_key))
                #     print("next_key: {0}, leftover_keys: {1}".format(next_key, leftover_keys))
                #     print(value, dicRef)
                #     print(self.finalFrank)
                # next key = interestRtContracts
                # curr key = monthlyReturnCats
                # key_values = {monthlyReturnCats: None}
                if isinstance(key_values, list): # search for the next_key
                    for item in key_values:
                        if isinstance(item, dict) and next_key in item.keys():
                            # next key found
                            val = dicRef[curr_key][next_key]
                            if not isinstance(val, dict):
                                dicRef[curr_key][next_key] = {}
                            self.writeValue(leftover_keys, dicRef[curr_key][next_key], value)
                        else:
                            # next key not found, create it 
                            if len(leftover_keys) == 0:
                                dicRef[curr_key][next_key] = value
                                return
                            dicRef[curr_key][next_key] = {}
                            self.writeValue(leftover_keys, dicRef[curr_key][next_key], value)
                        # key doesn't exist, so create
                elif isinstance(key_values, dict): # search for the next_key
                    if next_key in key_values.keys():
                        # next key found
                        val = dicRef[curr_key][next_key] # curr_key = identifiers, next_key = isin
                        # val = {'empty': {'value': 'US0189148044'}}
                        if isinstance(val, dict):
                            if len(leftover_keys) == 0:
                                # don't want to overrwrite
                                return
                            elif len(leftover_keys) == 1:
                                val[leftover_keys[0]] = value
                                return
                            else:
                                self.writeValue(leftover_keys, dicRef[curr_key][next_key], value)
                        else:
                            # its some value 

                            # no more keys, replace the value if it's not none
                            if len(leftover_keys) == 0:
                                if value != 'None':
                                    dicRef[curr_key][next_key] = value
                                return
                            # 1 more key, replace value with dict and create a key, assign value
                            elif len(leftover_keys) == 1:
                                dicRef[curr_key][next_key] = {}
                                dicRef[curr_key][next_key][leftover_keys[0]] = value
                                return
                            # 2 or more keys, replace value with dict & create key, go to next
                            else:
                                dicRef[curr_key][next_key] = {}
                                self.writeValue(leftover_keys, dicRef[curr_key][next_key], value)
                    else: # key was not found
                        if len(leftover_keys) == 0: # 
                            dicRef[curr_key][next_key] = value
                            return
                        dicRef[curr_key][next_key] = {}
                        self.writeValue(leftover_keys, dicRef[curr_key][next_key], value)                  
                else:
                    # something is already written here!
                    # key_values = None
                    # dicRef = { 'month': None , ... }
                    if len(leftover_keys) == 0:
                        dicRef[curr_key] = {}
                        dicRef[curr_key][next_key] = value
                        return
                    dicRef[curr_key] = {}
                    dicRef[curr_key][next_key] = {}
                    self.writeValue(leftover_keys, dicRef[curr_key][next_key], value) 
            else:
                if value != 'None':
                    dicRef[curr_key] = value
                    
    def countKeys(self, dic, count):
        for key, value in dic.items():
            if isinstance(value, dict):
                self.countKeys(value, self.count)
            else:
                self.count+=1

    def writeJSON(self):
        self.finalFrank = {}
        for chainedKeys, value in self.frankenstienJSON.items():
            # there will always be at least two keys
            keys = chainedKeys.split('-')
            if 'monthlyReturnCats' in keys:
                print(keys, 'about to write value')
            self.writeValue(keys, self.finalFrank, value)
        print("Final frank:")
        print(self.finalFrank)
        self.count = 0
        self.countKeys(self.finalFrank, 0)
        print(self.count)

    def unravelJSON(self, hash, prev_keys):
        for key, value in hash.items():
            curr_key = "{0}-{1}".format(prev_keys, key)
            if isinstance(value, dict):
                self.unravelJSON(value, curr_key)
            elif isinstance(value, list):
                for hash in value:
                    self.unravelJSON(hash, curr_key)
            else:
                if curr_key not in self.frankenstienJSON.keys():
                    self.frankenstienJSON[curr_key] = value
    # iterate through each k , v pair
    # if the v is a dictionary, 
    # pass in v and add the key to prev_keys
    # else write to the set with
    # key = prev_keys+curr_key
    # value = value 


if __name__ == '__main__':
    c = CIKJSONGenerator()
    c.parseKeysForCIK()
    # c.fetchAllCIKs()
    # c.fetchCIKData()
    c.writeJSON()
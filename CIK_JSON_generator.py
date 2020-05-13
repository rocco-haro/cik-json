import requests

class CIKJSONGenerator(object):
    def __init__(self):
        print("starting...")
        self.reportKeys = []
        self.frankenstienJSON = {}

    def fetchAllCIKs(self):
        r = requests.get('https://wsbnports.azurewebsites.net/odata/nports/FilerCiks')
        print(r.status_code)
        self.ciks = r.json()['value']
        print(self.ciks)

    def fetchCIKData(self):
        data = {}
        for cik in self.ciks:
            url = "https://wsbnports.azurewebsites.net/odata/nports('{}')?$count=true".format(cik)
            print(url)
            r = requests.get(url)
            print(r.status_code)
            print(r)
            try:
                cikInfo = r.json()['value']
                data[cik] = cikInfo
                print(data)
                return
            except:
                continue


    def iterdict(self, d):
        for k,v in d.items():
            if isinstance(v, dict):
                self.iterdict(v)
            elif k not in self.reportKeys:
                self.reportKeys.append(k)
            else:
                self.reportKeys.append(k)
                print(k)

    def parseKeysForCIK(self):
        url = "https://wsbnports.azurewebsites.net/odata/nports('0000081443')?$count=true"
        r = requests.get(url)
        data = r.json()['value']
        for report in data:
            #print(report.keys())
            self.iterdict(report)
            print(self.reportKeys)
            return


if __name__ == '__main__':
    c = CIKJSONGenerator()
    c.parseKeysForCIK()
    # c.fetchAllCIKs()
    # c.fetchCIKData()
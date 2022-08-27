import time, json, os
import pandas as pd



class Doc:
    attrs = {}
    dfs = {}



    def eval(self):
        if 'Tipo' not in self.attrs.keys():
            return
        tipo = self.attrs['Tipo']
        if tipo not in self.dfs.keys():
            self.dfs[tipo] = []
        tipo_arr = self.dfs[tipo]
        tipo_arr.append(self.attrs)
        self.dfs[tipo] = tipo_arr
        self.attrs = {}
        print(f"Current size: {len(json.dumps(self.dfs, indent=4))/1000}KB")



    def export(self, keyword):
        keyword = keyword.replace(' ', '_')
        # print(json.dumps(self.dfs, indent=4))
        directory = 'exports'
        if not os.path.exists(directory):
            os.makedirs(directory)
        for key in self.dfs.keys():
            df = pd.DataFrame(self.dfs[key])
            df.to_csv(f'exports/{keyword}_{key}_{round(time.time())}.csv', sep='&')
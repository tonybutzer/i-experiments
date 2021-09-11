import subprocess

def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    stupidBytesObject = proc_stdout
    outStr = (stupidBytesObject.decode("utf-8"))
    print(outStr)
    return(outStr)


class Fido:
    def __init__(self, src_asset, dst_path):
        self.src_asset = src_asset
        self.dst_path = dst_path


    def __repr__(self):
        #print(self.src_asset)
        #print(self.dst_path)

        rep = '{asset:' + self.src_asset + ',\npath:' + self.dst_path + '}'
        return rep


    def wget_asset(self):
        print("wget this: %s",self.src_asset)
        cmd = 'wget -nv -O- ' + self.src_asset + ' | aws s3 cp - ' + self.dst_path
        print(cmd)
        result = subprocess_cmd(cmd)
        print(result)


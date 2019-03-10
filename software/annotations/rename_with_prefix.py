import os
from glob import glob


if __name__ == '__main__':
    dirname = 'td5'
    pre = "%s-" % (dirname,)
    for f in glob("%s/*.jpg" % (dirname,)):
        path = f.split('\\')
        filename = '%s%s' % (pre, path[1])
        f2 = '\\'.join([dirname, filename])
        # [os.rename(f, "{}{}".format(pre, f)) ]
        os.rename(f, f2)
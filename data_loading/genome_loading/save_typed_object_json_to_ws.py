import simplejson
import time
import sys
import doekbase.workspace.client

def save_object(filename=None,wsname=None,wstype=None, wsurl=None): 
    with open(filename) as f:
        content = f.read()
#    input_file_handle = open(filename, 'r')
#    content = input_file_handle.read()
    ws = doekbase.workspace.client.Workspace(wsurl)

    start  = time.time()
    save_info = ws.save_objects({"workspace":wsname,"objects":[ { "type":wstype,"data":simplejson.loads(content),"name":filename}]})
    end = time.time()
    print  >> sys.stderr, " saving " + wstype + " to ws, elapsed time " + str(end - start)
if __name__ == "__main__": 
    import argparse 
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--filename', 
                        action='store', type=str, nargs='?', required=True) 
    parser.add_argument('--wsname', 
                        action='store', type=str, nargs='?', required=True)
    parser.add_argument('--wstype', 
                        action='store', type=str, nargs='?', required=True) 
    parser.add_argument('--wsurl', 
                        action='store', type=str, nargs='?', required=True) 
    args, unknown = parser.parse_known_args()

    try: 
        save_object(filename = args.filename, 
                    wsname = args.wsname,
                    wstype = args.wstype,
                    wsurl = args.wsurl) 
    except Exception, e: 
        print e;
        sys.exit(1) 
    sys.exit(0) 

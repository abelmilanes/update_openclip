# update_openclip

Python utility to append new version to Autodesk  OpenClip files

Suports Image sequences or movie files.


## Requirments
Python 3.xx

PyYAML

```bash
pip install PyYAML
```

## Usage

```bash
python update_openclip.py -f <openclip file> -i <versioned clip>
```
## Examples

```bash
python update_openclip.py -f shot_0010.clip -i shot_0010_comp_v01.1001.exr
```
```bash
python update_openclip.py -f shot_0010.clip -i shot_0010_comp_v01.mov
```
...

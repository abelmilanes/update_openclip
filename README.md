# update_openclip

Python utility to append new versions to Autodesk  OpenClip files

More information about Autodesk Openclip:

[Open Clip Reference](https://help.autodesk.com/view/FLAME/2025/ENU/?guid=Flame_API_Open_Clip_Reference_html)

## Features
- Standalone multi-platform
- Suports image sequences and movie files.
- YAML based presets for file location and versions entries


## Requirments
Python 3.xx

PyYAML

```bash
pip install PyYAML
```

## Usage

```
python update_openclip.py -f <openclip file> -i <versioned clip>
```

```
  -f FILE,              --file FILE  Openclip file
  
  -i INPUT,             --input INPUT
                        Image sequence or movie clip
                        
  -p FEED_PRESET,       --feed_preset FEED_PRESET
                        Openclip feed preset from YAML presets file
                        
  -m VERSION_PRESET,    --version_preset VERSION_PRESET
                        Openclip version preset from YAML presets file
                        
  -n, --dry_run         Print results but dont do anything
```

## Example Usage

```bash
python update_openclip.py -f shot_0010.clip -i shot_0010_comp_v01.1001.exr
```
```bash
python update_openclip.py -f shot_0010.clip -i shot_0010_comp_v01.mov
```

## Nuke Utils
### nuke_read.nk
Nuke Read node with extra functionality to read versions from Openclips feeds.

Currently only EXR sequences are suported

### nuke_write.nk
Nuke Write node with extra functionality to append versions to Openclips feeds.

Openclip file path should be stored in the stream as a ```nuke/flame/openclip``` metadata key.





...

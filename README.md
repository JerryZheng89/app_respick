# App-Resister picker
## Power Divider Resistor picker


## Clone
```shell
git clone https://github.com/JerryZheng89/app_respick.git
git submodule update --init --recursive
```


## build
## Linux 
```shell
```

## MacOS
```shell
pyinstaller --windowed --icon="icons/icon.icns" --add-data="img/respick_dcdc.svg:img" --add-data="icons/respick_splash.png:icons" app_respick.py
```

## Windows
```shell
pyinstaller --onefile --windowed --icon="icons/icon.ico" --add-data="img/respick_dcdc.svg:img" --add-data="icons/respick_splash.png:icons" app_respick.py
```
```
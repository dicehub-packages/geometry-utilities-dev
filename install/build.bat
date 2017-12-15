ECHO %1 
set PY=%1

cd %~dp0

%PY% -m pip wheel --wheel-dir dist ^
http://backup1.foxcloud.net/mcubcsro/public/dice/wheels/numpy_stl-2.3.2-cp36-cp36m-win_amd64.whl ^
http://backup1.foxcloud.net/mcubcsro/public/dice/wheels/pythonocc_core-0.18.0-cp36-cp36m-win_amd64.whl ^
http://backup1.foxcloud.net/mcubcsro/public/dice/wheels/vtk-8.0.0-cp36-cp36m-win_amd64.whl ^
https://github.com/dicehub/dice_tools/archive/17.12.0.zip ^
https://github.com/dicehub/dice_vtk/archive/17.12.0.zip

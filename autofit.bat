
python c:\Users\peter\Documents\Dev\fit-indoor-fix\analyzeWktInFit.py auto %1
goto done

set file_list=

:loop
if "%~1"=="" goto done
set file_list=%file_list% "%~1"
shift
goto loop

rem Replace "YourExecutable.exe" with the path to your actual command
rem python c:\Users\peter\Documents\Dev\fit-indoor-fix\analyzeWktInFit.py auto %file_list%

:done
pause
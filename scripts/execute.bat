REM Changing to bat file directory
CD %~dp0

REM Change to project directory
CD ..

REM LOG
SET logdate=%date:~11,4%-%date:~8,2%-%date:~5,2%
SET path=\log\
SET filename=%path%log-%logdate%.log
ECHO ==LOG FILE %logdate% == > %filename%

REM Switch to production
GIT CHECKOUT MAIN >> %filename%
REM Activating environment
CALL .\amazon_webscrap\Scripts\activate >> %filename%
REM Print timestamp
SET isodate=%date:~11,4%-%date:~8,2%-%date:~5,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
ECHO Amazon Webscraping starts at %isodate% >> %filename%
REM Get all arguments after executions
CALL python .\src\amazon_webscraping.py %* >> %filename%
REM Print timestamp
SET isodate=%date:~11,4%-%date:~8,2%-%date:~5,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
ECHO Amazon Webscraping ends succesful at %isodate% >> %filename%

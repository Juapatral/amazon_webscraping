REM Changing to bat file directory
CD %~dp0

REM Change to project directory
CD ..

REM Switch to production
CALL git checkout main

REM Activating environment
CALL .\amazon_webscrap\Scripts\activate

REM Print timestamp
SET isodate=%date:~11,4%-%date:~8,2%-%date:~5,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
ECHO Amazon Webscraping starts at %isodate%

REM Get all arguments after scripts
CALL python .\src\amazon_webscraping.py %*

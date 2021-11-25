REM Changing to bat file directory
CD %~dp0
REM Change to project directory
CD ..
REM Activating environment
CALL .\amazon_webscrap\Scripts\activate
ECHO "Amazon Webscraping starts"
REM Get all arguments after executionss
CALL python .\src\amazon_webscraping.py %*
ECHO "Amazon Webscraping ends"

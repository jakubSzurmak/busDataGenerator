Due to the use of libraries as beautifullsoup4 and requests in order to scrape and 
gather data about bus variants from wikipedia we append 2 versions of generator.
One called "generator_with_internet" and the second one "generator_without_internet"
if the user doesn't have internet connection he has to use the second one. 
The generator applications have at most 2 fixed dependencies both of them need the
"serviceList.bulk" which is pregenerated by us from online sources as we didn't want
services to be randomly selected from a set LoremIpsum1...LoremIpsumN. 
Generator without internet also has the "variants.bulk" file appended as the result
of "generator_with_internet".
Due to size limitations on enauczanie we append only internet version of generator.
If the user has not internet acess, he has to launch it manually via python interpreter.
To obtain no internet version visit and download
https://drive.google.com/file/d/1ptc7_-nKdmwWM95LTTp7D-vJeJtBbg-P/view?usp=sharing
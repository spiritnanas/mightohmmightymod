# mightohmmightymod
A Pi Pico Mod for the MightOhm Geiger Counter Kit

Parts:

1) https://www.amazon.com/gp/product/B072Q2X2LL/ref=ppx_yo_dt_b_asin_title_o09_s00?ie=UTF8&psc=1
2) https://www.amazon.com/gp/product/B09DPMQ1F3/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1
3) https://www.amazon.com/gp/product/B00NAY2NAI/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1
4) https://www.amazon.com/gp/product/B093PJ2NJZ/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
5) https://www.amazon.com/gp/product/B08RMQP6YP/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&th=1
6) https://www.amazon.com/gp/product/B07CKLNR2T/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1
7) https://mightyohm.com/blog/products/geiger-counter/

Step 1) Connect all components as discussed in the pinout document under the Documentation section. I used the item under the 5th Amazon link to make detachable cables for easy component replacement. 

Step 2) Print all files in the STL folder.

Step 3) Attach components from step 1 to the midplate.

Step 4) Set up Pi Pico for use with MicroPython. I used Thonny. Simply install Thonny. Once installed, plug the Pi in with the boot select button held down. Thonny should suggest the installation of the required files for MicroPython onto the Pi. 

Step 5) Use Thonny to copy the main.py, sdcard.py and the lib folder to the Pi Pico. 

Step 6) Power on the Pi Pico, it should boot up and load the application. 

Step 7) Once you test everything, use #4-40x3/4" to affix the pieces together. The printed components screw into the standoffs included in the MightyOhm kit. 

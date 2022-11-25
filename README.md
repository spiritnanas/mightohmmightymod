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

Step 1) Connect all components as discussed in the pinout document under the Documentation section. I used the item under the 5th Amazon link to make detachable cables for easy component replacement. To connect the Pi to the MightyOhm I used a custom cable, made using the below steps:

      1) Cut a GPIO jumper cable, leaving about 3/4" of wire. You want to use the female side of the cable for this purpose. 
      2) Remove the plastic housing from the connector using side cutters. Be careful here to avoid cutting the wire inside.
      3) Use heatshrink around the remaining metal connector. 
      4) Strip about 1/8" of the wire from the GPIO cable.
      5) Now, using the cable kit (item 6 on the purchase list), create a 2 wire cable, attaching both a female end and male end. 
      6) Cut this cable in half.
      7) Add heat shrink to one half of the cable.
      8) Solder one end of the newely cut in half cable to the GPIO cable.
      9) Solder the remaining cable to the Pi Pico, making reference to the pinout documentation in the Documentation section. 

Step 2) Print all files in the STL folder.

Step 3) Attach components from step 1 to the midplate.

Step 4) Set up Pi Pico for use with MicroPython. I used Thonny. Simply install Thonny. Once installed, plug the Pi in with the boot select button held down. Thonny should suggest the installation of the required files for MicroPython onto the Pi. 

Step 5) Use Thonny to copy the main.py, sdcard.py and the lib folder to the Pi Pico. 

Step 6) Power on the Pi Pico, it should boot up and load the application. 

Step 7) Once you test everything, use #4-40x3/4" to affix the pieces together. The printed components screw into the standoffs included in the MightyOhm kit. 

Demo Videos:

https://www.youtube.com/shorts/H37LoZpWwPw

https://www.youtube.com/watch?v=6j20wASLf7Y

Reference Pictures:

![IMG_0333](https://user-images.githubusercontent.com/118999263/203877978-4ca4c1a1-4ab0-4144-ad73-19199ea3d9b2.jpeg)

![IMG_0346](https://user-images.githubusercontent.com/118999263/203877989-61a0076b-e78d-45ed-b960-32e18d5fa310.JPG)

![IMG_0334](https://user-images.githubusercontent.com/118999263/203877999-b6fe1c10-d57e-45d5-ba93-95b97692edf8.jpeg)

![IMG_0338](https://user-images.githubusercontent.com/118999263/203878005-e648ba02-c0b3-4b4d-baf3-4961ed177ec4.jpeg)

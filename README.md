# AI-FIGBOT
Giafigures game variant developed for the <strong>Artificial Intelligence</strong> class using a Lego EV3 Built Robot.
* IA-FIG-1.py -> 1st Phase -> The Robot moves all directions, rotates and does random routes

## Index
* Lego EV3 Robot Build
* How this Game Works
* Heuristics for the Game
* Game showcase on the EV3 Robot

### Lego EV3 Robot Build
Starting on this project, we used this EV3 guide as a basis for the robot construction (link):
https://assets.education.lego.com/v3/assets/blt293eea581807678a/blt8b300493e30608e9/5f8801dfb8b59a77a945d13c/ev3-rem-color-sensor-down-driving-base.pdf?locale=en-us

After making a few adjustments on the construction during this project, here is the final result of the EV3 build:
![EV3 Build](https://github.com/andrecfoss/AI-FIGBOT/assets/134842813/10d4fe15-a5f7-4759-a941-b44ce7eb776e)

The main changes we made where:
* Instead of the color sensor facing downwards like is shown on the guide, we decided to just locate it on the side, being easier to read the colors but also because of the claw we created.
* The claw created here had the idea to drag an object on the grid instead of grabbing, as we thought on the programming side would be easier for us.
* We developed a mechanism in which consists of 3 wheels, positioning the rotation motor on top of the EV3, in order for this motor to move the claw up and down, when told so on the program.
* We decided to not include the <b>Gyroscope sensor</b>, since we had the gyro sensor integrated already on the left and right motors of the EV3. There were downsides on the usage of both being:
  - Using the Gyroscope Sensor is giving a very precise rotation movement for the EV3 but, on the coding side makes it much more difficult because of some of the libraries that the sensor uses causing trouble on the code.
  - The Gyro sensor on the motors are less precise, but helps on the coding side of the EV3, saving a lot of time trying to debug code issues.
    
<hr>

### How does this Giafigures Game Variant Work?

This game basically consists of 4 symbols being this ones: <h3>- O + X</h3>
We decided to lable each symbol for the EV3:

<table>
  <tr>
    <th>Symbol</th>
    <th>Block Number on the Grid</th>
    <th>Block Color</th>
  </tr>
  <tr>
    <th><b>O</b></th>
    <th>2</th>  
    <th>Blue</th>  
  </tr>
  <tr>
    <th><b>+</b></th>
    <th>3</th>  
    <th>Yellow</th>  
  </tr>
  <tr>
    <th><b>-</b></th>
    <th>4</th>  
    <th>Red</th>  
  </tr>
  <tr>
    <th><b>X</b></th>
    <th>5</th>  
    <th>Green</th>  
  </tr>
</table>
NOTE: The Number 0 on the grid represents a free position which means does not have a block on that position. 
The Number 1 was not used in this representation.

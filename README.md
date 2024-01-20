# AI-FIGBOT
Giafigures game variant developed for the <strong>Artificial Intelligence</strong> class using a Lego EV3 Built Robot.
<br> Graded <strong>17</strong>/20.

* IA-FIG-1.py -> 1st Phase -> The Robot moves all directions, rotates and does random routes according to the finding path algorithm A*

## Index
* How this Game Works
* Lego EV3 Robot Build
* Heuristics for the Game
* Game showcase on the EV3 Robot

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
NOTE: <br>
Number 0: Free position on the Grid <br>
<s>Number 1: Not used</s> <br>

<p> <strong>The main goal</strong> of this game is to form complete figures using the same blocks for each figure. There are small figures that can be formed but also bigger figures.</p>

#### Small Figures

![IA - Small Figures](https://github.com/andrecfoss/AI-FIGBOT/assets/134842813/e50366cc-615f-486f-bbff-97c169c7af4a)


#### Bigger Figures

![IA - Bigger Figures](https://github.com/andrecfoss/AI-FIGBOT/assets/134842813/0d73bc5a-ba7e-433d-8a4a-74864168c20a)

For every figure that is formed on the Grid, will have this sequence:

![IA - Game Sequence](https://github.com/andrecfoss/AI-FIGBOT/assets/134842813/740b5fae-232b-4b76-877c-ead1888217db)

Every time the EV3 forms a complete figure, it eliminates from the grid and retrieves points. <br>
NOTE: The Game sequence has a limited amount of blocks, at the end of the game there can be blocks left on the grid which result of figures that were not completely formed.

#### Point System
For every figure that is completed and eliminated from the grid, we have a point system that being:
* The points for every figure formed consists of the formula <strong>2^(Number of blocks to form figure)</strong>.
  - For example, if we form a Small Figure for the + there is 5 blocks, so 2^5 = 32 points.
* At the end of the game, if there are blocks left on the grid we use the following formula:
  - <strong>2^(Number of blocks to form figure) - 2^(Number of blocks left on the grid)</strong>

<hr>

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

## What kind of Heuristics where developed for this Game?

Before we started creating the Heuristics, we had in mind this Rule, which was to compare 2 heuristics on this Game, based on these goals:
- One Heuristic that could deliver the most points, but take more risks
  - For example, there could be positions on the grid where the EV3 could not place blocks because it would have been blocked by others blocks already placed.
- Another Heuristic that delivered less points, but would safely run the whole block sequence to form the figures, without blocking the EV3 on the Grid.

SO, with these goals in mind, here are the Two Heuristics we developed:

### Predefined Maps

### Search Tree

We also developed a Third Heuristic that calculates the path where the next block is going to be placed on the Grid. For that we used the A* Algorithm as a basis.


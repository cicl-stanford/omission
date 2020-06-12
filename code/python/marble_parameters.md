# World setup in the different experiments 

## Exp 1: Basic setup 

- global parameters: 
	+ var fullX = 8
	+ var fullY = 6
	+ var speed = 2

- ball positions: 
	+ ball A: 
		* x = fullX - 0.5 
		* y = fullY - 1
	+ ball B (misses): 
		* x = fullX - 0.5 
		* y = 1 
		* velx = -1 * speed
		* vely = 0.5 * speed
	+ ball B (hits): 
		* x = fullX - 0.5 
		* y = fullY/2
		* velx = -1 * speed
		* vely = 0 * speed

## Exp 2: With moving wall 

## Exp 3: Three ball setup 

- global parameters: 
	+ WIDTH = 800

- Ball positions
	+ world.setBall1(x = 780, y = 60, xvel = -3.5, yvel = 0.83, delay = 0); // green ball (top)
	+ world.setBall2(x = 80, y = 300, xvel = 0, yvel = 0, delay = 0);
	+ world.setBall3(x = 780, y = 540, xvel = -3.5, yvel = -1.5, delay = 200); // blue ball (bottom)

- horizontal barrier: 
	+ var horizontalWallBody: b2Body = createWalls(positionX = WIDTH, positionY = 155, halfwidth = (WIDTH / 1.95), halfheight = (20 / 2), userdata = "horizontalWall");

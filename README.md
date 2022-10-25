## README
This is the code base of the our groups EE403w project

Project manager: Erik Huuki

## Front End
the front end is essentially a state machine, which uses Qt to handle graphics and user inputs.

### State Class
The `State` class contains the current state of the application.
it provides methods which can be used to modify the state, or be bound
to commands which are then typed by the user.

this design pattern allows the interface type to be easily interchangable (ie, output
using curses to terminal, create a custom window with a graphcis library such as WebGPU
or OpenGL and draw to a pixel buffer, or use Qt, which is what this project uses.)

### Command Class
Every command is a subclass of the the `Command` class. One instance of each command subclass must be created.
Upon instantiation, each instance stores a reference to itself in a static parameter of the `Command` class.

when a command is entered, this static list stored in `Command` is queried, and any function or data associated
with the subclass can be gathered.

### Exp Class
`Exp` class is an extension of the axioms_2 `expr` class. `Exp` in addition to everything that `expr` does, `Exp`
allows previously defined expressions to be referenced in new expressions, through special functions.

# KnotTheory

# Restrictions of Image
 - Can't have different arcs touching eachother
 - The space between crossings should be relatively equal
   - assuming they are, this is a good way to detect if we passed the endpoint we were looking for
   - maybe have it to do with the line thickness?

# Ideas
 - Maybe not necessary to do BFS on all pixels of an arc? Just find the boundary?
 - Could do that by BFSing the background, going one pixel in on the found arcs, and those are are the boundary points
 - For links, the knots might be different colors. Add component functionality
 - 3D seifert surfaces plots using matplotlib
 - http://hmeine.github.io/qimage2ndarray/ instead of files
 - separating spheres
 - generate a knot given crossing index
 - using DT notation to find a knot
    - https://knotinfo.math.indiana.edu/descriptions/dt_notation.html
    - https://knotinfo.math.indiana.edu/index.php 
    - https://knotinfo.math.indiana.edu/homelinks/cite_info.html
 - draw a knot, take a pic, get a link to the knot on knotinfo (this would be the simplest form knot; then show info on the knot diagram itself)
 - https://math.okstate.edu/people/segerman/talks/drawing_knots.pdf
 

## To Connect Endpoints
 - check distance from the endpoints and the intersection (intersection should be relatively equadistant between endpoints)
 - try all orientations of all arcs in any order ... this would get you all potential orderings... which are just all of them lmao
 - check to make sure endpoints cross over (close to perpendicular) to another rope
 - just go down a rope and check all sides of it for endpoints of other ropes (directionality would still be better)
 - when using first derivative to get slope, get as close as you can do perpendicular against the end boundary of the line
 - intersection likely to be near another line

## Credit:
# StackOverflow
 - 
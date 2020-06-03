# KnotTheory

# Restrictions of Image
 - Can't have different arcs touching eachother
 - The space between crossings should be relatively equal
   - assuming they are, this is a good way to detect if we passed the endpoint we were looking for
   - maybe have it to do with the line thickness?

# Ideas
 - BEFORE SKELETON ANALYSIS, GO THRU AND REMOVE EVERY UNCESSARY PIXEL, SO LIKE 
 ```
    101
    010
    011
 ```
    would become
 ```
    101
    010
    001
 ```
 idk what that'd fix but it would fix something
 - Maybe not necessary to do BFS on all pixels of an arc? Just find the boundary?
 - Instead of using equality to asses which spines to cut, use how close they are to the end too
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
 
 - currently, every crossing needs to have an i, j, and k. Not implied like an arc jumping over two arcs instead of one.

## To Connect Endpoints
 - check distance from the endpoints and the intersection (intersection should be relatively equadistant between endpoints)
 - try all orientations of all arcs in any order ... this would get you all potential orderings... which are just all of them lmao
 - check to make sure endpoints cross over (close to perpendicular) to another rope
 - just go down a rope and check all sides of it for endpoints of other ropes (directionality would still be better)
 - when using first derivative to get slope, get as close as you can do perpendicular against the end boundary of the line
 - intersection likely to be near another line


 - has a problem with small arcs for some reason
 - assumption: i0 and j dirs must arrive at an i1 and i1, k dirs must arrive at i0 crossings


- always trying to balance computation on the fly vs computation on changes, like with
being able to quickly compute crossings between or keeping track of the "flipped" knot so that
r1 crossing detection becomes trivial, it's the same arc on either one or the other.
keeping arc neighbors would do this too.
- probably would have been easier to represent each edge from a vertex to another as a distinct
  "arc", even if the crossing is an "i". Then have a function to compute the "names" of the arcs
  on the fly.
- tough to figure out incoming dir for unknots or loops, there is background that you need about knots
- propogate crossing change function?

## Credit:
# StackOverflow
 - 